from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
import requests
from django.db import IntegrityError
from django.urls import reverse
from .models import *
from datetime import datetime
from openai import OpenAI
from django.db.models import Avg, Count


def index(request):
    return render(request, "index.html")



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmPassword"]

        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")
    

@login_required
def speech_to_text(request):
    return render(request, 'speech_to_text.html')


@login_required
def save_transcript(request):
    if request.method == 'POST':
        transcript = request.POST.get('transcript')
        subject = request.POST.get('subject')
        chapter = request.POST.get('chapter')
        curr_user = request.user
        SpeechData.objects.create(user=request.user, subject=subject, chapter=chapter, text=transcript)
        data = {
            "subject":subject,
            "chapter":chapter,
            "transcript":transcript,
            "curr_user":curr_user
        }
        print("\n\nnote saved successfully\n\n")
        create_notes(data)
        return redirect('index')
    

def create_notes(data):
    print("in create notes function")
    subject = data["subject"]
    print(f"\nSubject: {subject}\n")
    chapter = data["chapter"]
    print(f"\nSubject: {chapter}\n")
    transcript = data["transcript"]
    print(f"\nSubject: {transcript}\n")
    curr_user = data["curr_user"]
    print(f"\nSubject: {curr_user}\n")

    custom_message = f"Provide some extra information in notes too. Create proper notes with heading. make notes point wise too. The data is: {transcript}"
    API_KEY = "API_KEY"
    client = OpenAI(
        api_key=API_KEY
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": custom_message}
        ]
    )
    reply = response.choices[0].message.content.strip()
    # reply = transcript
    date = datetime.now()
    notes = reply
    print(reply)

    Notes.objects.create(user=curr_user, subject=subject, chapter=chapter, notes=notes, date=date)
    print("Saved the ai notes")


@login_required
def subject_based_notes(request):
    all_notes = Notes.objects.all()

    available_subjects = []
    available_chapters = {}

    for notes in all_notes:
        if notes.subject not in available_subjects:
            available_subjects.append(notes.subject)
            available_chapters[notes.subject] = []

        if notes.chapter not in available_chapters[notes.subject]:
            available_chapters[notes.subject].append(notes.chapter)

    all_notes_json = serializers.serialize('json', all_notes)

    return render(request, "notes.html", {
        "all_notes_json": all_notes_json,
        "available_subjects": available_subjects,
        "available_chapters": available_chapters
    })


@login_required
def AI_Quiz(request):
    all_quiz = Quiz.objects.all()

    available_subjects = []
    available_chapters = {}

    for quiz in all_quiz:
        if quiz.subject not in available_subjects:
            available_subjects.append(quiz.subject)
            available_chapters[quiz.subject] = []

        if quiz.chapter not in available_chapters[quiz.subject]:
            available_chapters[quiz.subject].append(quiz.chapter)

    all_quiz_json = serializers.serialize('json', all_quiz)

    return render(request, "aiQuiz.html", {
        "all_quiz_json": all_quiz_json,
        "available_subjects": available_subjects,
        "available_chapters": available_chapters
    })


@login_required
def dashboard(request):
    quiz_data = QuizScorecard.objects.all()

    subjects = []
    for quiz in quiz_data:
        if quiz.subject not in subjects:
            subjects.append(quiz.subject)

    subj_chap = {}
    for quiz in quiz_data:
        if quiz.subject not in subj_chap:
            subj_chap[quiz.subject] = [quiz.chapter]
        else:
            subj_chap[quiz.subject].append(quiz.chapter)

    pie_chart_no_of_attempts_per_subject = {}
    for quiz in quiz_data:
        if quiz.subject not in pie_chart_no_of_attempts_per_subject:
            pie_chart_no_of_attempts_per_subject[quiz.subject] = 1
        else:
            pie_chart_no_of_attempts_per_subject[quiz.subject] += 1

    line_chart_per_subject = {}
    for quiz in quiz_data:
        if quiz.subject not in line_chart_per_subject:
            line_chart_per_subject[quiz.subject] = {}
            line_chart_per_subject[quiz.subject][quiz.date_recorded] = quiz.score
        else:
            line_chart_per_subject[quiz.subject][quiz.date_recorded] = quiz.score


    line_chart_per_subject_data = []
    for subject, subject_data in line_chart_per_subject.items():
        line_chart_per_subject_data.append((subject, list(subject_data.items())))

    summary_table_data = []
    for subject, chapters in subj_chap.items():
        for chapter in chapters:
            quizzes = quiz_data.filter(subject=subject, chapter=chapter)
            total_attempts = quizzes.count()
            average_score = sum(quiz.score for quiz in quizzes) / total_attempts if total_attempts > 0 else 0
            summary_table_data.append({
                'subject': subject,
                'chapter': chapter,
                'average_score': average_score,
                'total_attempts': total_attempts,
            })

    return render(request, "dashboard.html", {
        "summary_table_data": summary_table_data,
        "pie_chart_no_of_attempts_per_subject": pie_chart_no_of_attempts_per_subject,
        "line_chart_per_subject_data": line_chart_per_subject_data,
    })

    # quiz_data = QuizScorecard.objects.all()
    # subjects = []
    # for quiz in quiz_data:
    #     if quiz.subject not in subjects:
    #         subjects.append(quiz.subject)
    #
    # quiz_data_json = serializers.serialize('json', quiz_data)
    #
    # # Get average score and total attempts for each subject and chapter
    # subject_data = []
    # for subject in subjects:
    #     chapters = QuizScorecard.objects.filter(subject=subject).values('chapter').distinct()
    #     for chapter in chapters:
    #         avg_score = QuizScorecard.objects.filter(subject=subject, chapter=chapter['chapter']).aggregate(Avg('score'))['score__avg']
    #         total_attempts = QuizScorecard.objects.filter(subject=subject, chapter=chapter['chapter']).aggregate(Count('score'))['score__count']
    #         subject_data.append({
    #             'subject': subject,
    #             'chapter': chapter['chapter'],
    #             'avg_score': avg_score,
    #             'total_attempts': total_attempts
    #         })
    #
    # return render(request, 'dashboard.html', {'quiz_data_json': quiz_data_json, 'subjects': subjects, 'subject_data': subject_data})


@login_required
def saveScore(request):
    if request.method == "POST":
        data = request.POST

        subject = data.get('subject')
        chapter = data.get('chapter')
        score = data.get('score')
        if(subject and chapter):
            QuizScorecard.objects.create(user=request.user, subject=subject, chapter=chapter, score=score)
        return redirect('index')


@login_required
def tmp(request):
    all_quiz = Quiz.objects.all()

    available_subjects = []
    available_chapters = {}

    for quiz in all_quiz:
        if quiz.subject not in available_subjects:
            available_subjects.append(quiz.subject)
            available_chapters[quiz.subject] = []

        if quiz.chapter not in available_chapters[quiz.subject]:
            available_chapters[quiz.subject].append(quiz.chapter)

    all_quiz_json = serializers.serialize('json', all_quiz)

    return render(request, "tmp.html", {
        "all_quiz_json": all_quiz_json,
        "available_subjects": available_subjects,
        "available_chapters": available_chapters
    })
    # all_quiz = Quiz.objects.all()
    #
    # available_subjects = []
    # available_chapters = {}  
    #
    # for quiz in all_quiz:
    #     if quiz.subject not in available_subjects:
    #         available_subjects.append(quiz.subject)
    #         available_chapters[quiz.subject] = []
    #
    #     if quiz.chapter not in available_chapters[quiz.subject]:
    #         available_chapters[quiz.subject].append(quiz.chapter)
    #
    # all_quiz_json = serializers.serialize('json', all_quiz)
    #
    # return render(request, "tmp.html", {
    #     "all_quiz_json": all_quiz_json,
    #     "available_subjects": available_subjects,
    #     "available_chapters": available_chapters
    # })