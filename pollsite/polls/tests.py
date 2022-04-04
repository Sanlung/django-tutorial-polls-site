import datetime
from os import popen

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

# Test the Question model
class QuestionModelTests(TestCase):
    """tests on the Question model"""
    def test_was_published_recently_with_future_question(self):
        """'was_published_recently' returns False when a question's pub_date is in the future"""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """'was_published recently' returns False when a question's pub_date is older than one day"""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """'was_published_recently' returns True when a question's pub_date is within the last day"""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

# Test views
def create_question(question_text, days):
    """
    Create a question with the given `question_text` which is published the given number of `days` offset to now (negative for questions published in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    """test the IndexView view"""
    def test_no_questions(self):
        """displays appropriate message if no question exists"""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.'
        )
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """displays questions with a pub_date in the past on the index page"""
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_future_question(self):
        """questions with a pub_date in the future are not diaplayed"""
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """displays only past questions even if both past and future questions exist"""
        question = create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])


    def test_two_past_questions(self):
        """displays multiple past questions"""
        question1 = create_question(question_text="Past question 1", days=-30)
        question2 = create_question(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question1, question2])

class QuestionDetailViewTests(TestCase):
    """test the DetailView view"""
    def test_future_question(self):
        """returns 404 not found for a question with a pub_date in the future"""
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:detail', args=(future_question.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """displays the text of a question with a pub_date in the past"""
        past_question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:detail', args=(past_question.id))
        response = self.client.get(url)
        self.assertEqual(response, past_question.question_text)

# Test ResultView
class QuestionResultsViewTests(TestCase):
    """test the ResultsView view"""
    def test_future_question(self):
        """returns 404 not found for a question with a pub_date in the future"""
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:results', args=(future_question.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """displays the text of a question with a pub_date in the past"""
        past_question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:results', args=(past_question.id))
        response = self.client.get(url)
        self.assertEqual(response, past_question.question_text)
