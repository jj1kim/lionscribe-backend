import os
import queue
import threading
import time

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Job
from .pdf import render_markdown_to_pdf
from .serializers import (
    UserSerializer,
    SignupSerializer,
    JobSerializer,
    JobCreateSerializer,
)


# 작업 큐 — 백그라운드 워커 스레드가 여기서 pop해 PDF 생성을 처리한다.
_pdf_queue: queue.Queue = queue.Queue()


def _pdf_worker():
    """무한 루프 — 큐에서 job_id를 받아 PDF로 변환."""
    while True:
        job_id = _pdf_queue.get()
        try:
            job = Job.objects.get(pk=job_id)
            job.status = 'processing'
            job.save()

            pdf_bytes = render_markdown_to_pdf(job.input_text, title=job.title)
            job.result_file.save(
                f'{job.id}.pdf',
                ContentFile(pdf_bytes),
                save=False,
            )
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
        except Exception as e:
            try:
                job = Job.objects.get(pk=job_id)
                job.status = 'failed'
                job.error_message = str(e)[:500]
                job.save()
            except Exception:
                pass


# 모듈 import 시점에 워커 스레드 1개 시작 (gunicorn worker마다)
threading.Thread(target=_pdf_worker, daemon=True).start()


def _issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(_issue_tokens(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {'detail': '이메일 또는 비밀번호가 잘못되었습니다.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(_issue_tokens(user))


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class JobView(APIView):
    """
    GET — 내 작업 목록.
    POST — 마크다운 보고서를 받아 백그라운드 PDF 변환 작업으로 등록한다.
    응답은 즉시 (status=pending)이고, 실제 변환은 워커 스레드가 큐에서
    pop해서 처리한다.
    """

    def get(self, request):
        qs = Job.objects.filter(user=request.user)
        return Response(
            JobSerializer(qs, many=True, context={'request': request}).data
        )

    def post(self, request):
        serializer = JobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        job = Job.objects.create(
            user=request.user,
            title=data['title'],
            input_text=data['input_text'],
            status='pending',
        )
        _pdf_queue.put(job.id)
        return Response(
            JobSerializer(job, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class JobDetailView(APIView):
    def get(self, request, pk):
        try:
            job = Job.objects.get(pk=pk, user=request.user)
        except Job.DoesNotExist:
            return Response(
                {'detail': '작업을 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(JobSerializer(job, context={'request': request}).data)


class ChaosRestartView(APIView):
    """
    챌린지 채점기가 백엔드를 강제 종료시킬 때 호출하는 endpoint.
    `X-Chaos-Token` 헤더가 settings의 CHAOS_TOKEN과 일치할 때만 작동한다.
    응답을 보낸 직후 0.5초 후 프로세스를 죽인다.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.headers.get('X-Chaos-Token', '')
        if not settings.CHAOS_TOKEN or token != settings.CHAOS_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        def kill():
            time.sleep(0.5)
            os._exit(1)

        threading.Thread(target=kill, daemon=True).start()
        return Response({'status': 'restarting'})
