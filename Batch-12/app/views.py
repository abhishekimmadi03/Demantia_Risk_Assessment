from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime
from .models import *
import random
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Max, Min, Count, Q , Sum

def main(request):
    return render(request,'main/main.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = User.objects.filter(username=username).first()
        
        if not user:
            return render(request, "user/user_login.html", context={"msg": "Invalid User"})
        if user.status != "APPROVED":
            if user.status == "BLOCKED":
                msg = "user is blocked and cannot log in."
            else:
                msg = "user needs to be approved by the admin."
            messages.error(request, msg)
            return redirect('user_login')

        if user.password == password:
            request.session['user_id'] = user.id
            request.session['user_username'] = user.username
            request.session['user_age'] = user.age  # Store user age for filtering questions

            # Determine the age group based on user age
            if user.age < 30:
                request.session['age_group'] = 'Under 30'
            elif 30 <= user.age <= 60:
                request.session['age_group'] = '30-60'
            elif 60 < user.age <= 90:
                request.session['age_group'] = '60-90'
            else:
                request.session['age_group'] = '90+'

            return redirect("user_dashboard")  # Redirect to word recall pag
        
        else:
            return render(request, "user/user_login.html", context={"msg": "Invalid credentials"})

    return render(request, "user/user_login.html")


def user_signup(request):
    if request.method=="POST":
        username=request.POST.get("username","")
        password=request.POST.get("password","")
        email=request.POST.get("email","")
        phone_number=request.POST.get("phone_number","")
        age=request.POST.get("age","")
        image=request.FILES.get("image","")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please try with another email.")
            return redirect('user_login') 
    
        user = User(
                username=username,
                email=email,
                password=password, 
                image=image,
                age=age,
                phone_number=phone_number,
            )
        user.save() 
    
        messages.success(request, "Account created successfully!")
        return redirect('user_login') 
    return render(request, "user/user_signup.html")

def approve_user(request):
    if request.method=="POST":
        id = request.POST.get("id", 0)
        user = User.objects.get(id=int(id))
        user.is_approved=True
        user.is_blocked=False
        if user.status == 'APPROVED':
                messages.warning(request, f"User {user.username} is already approved")
        else:
                user.status = 'APPROVED'
                user.save()
                messages.success(request, f"User {user.username} has been approved!")
    return redirect("manage_user")

def block_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        user = User.objects.filter(id=user_id).first()
        user.is_approved=False
        user.is_blocked=True
        if user:
            user.status = 'BLOCKED'
            user.save()
            messages.success(request, f'user {user.username} has been blocked successfully.')
        else:
            messages.error(request, 'user not found.')
        
    return redirect('manage_user')

def manage_user(request):
    data = User.objects.filter().values(
        "id",
        "username",
        "email",
        "status",
        "age",
        "is_approved",
        "is_blocked",
        )
    return render(request, "admin1/manage_user.html" ,context={"data":list(data)})

def admin_login(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        if username == 'admin' and password == '123':

            request.session['admin_name'] = username
            return redirect("admin_dashboard")
        messages.error(request,'Invalid Username and Password')
        return render(request,'admin1/admin_login.html')
    return render(request,'admin1/admin_login.html')   



def admin_dashboard(request):
    user_count = User.objects.count()
    
    # Count tests for each type
    number_memory_count = NumberMemoryResult.objects.count()
    word_recall_count = WordRecallResult.objects.count()
    fluency_test_count = FluencyTestResult.objects.count()
    
    # Optional: Additional statistics, such as average scores or latest results, can be added here
    
    context = {
        'user_count': user_count,
        'number_memory_count': number_memory_count,
        'word_recall_count': word_recall_count,
        'fluency_test_count': fluency_test_count,
    }
    
    return render(request, 'admin1/admin_dashboard.html', context)


def user_dashboard(request):
    return render(request,'user/user_dashboard.html')



def add_users(request):
    if request.method == 'POST':
        username=request.POST.get("username","")
        password=request.POST.get("password","")
        email=request.POST.get("email","")
        phone_number=request.POST.get("phone_number","")
        image=request.FILES.get("image","")
        age=request.POST.get("age","")

        user = User.objects.create(
            username=username,
                email=email,
                password=password, 
                image=image,
                age=age,
                phone_number=phone_number,
        )
        user.save()
        messages.success(request, "User added successfully!")
        return redirect('add_users')

    return render(request, 'admin1/add_users.html') 


import re
from datetime import datetime

def clean_word(word):
    return re.sub(r'[^\w\s]', '', word).strip().lower()

# def attempt_test(request):
#     # Check if the user is logged in by checking the session
#     if not request.session.get('user_id'):
#         return redirect('user_login')  # Redirect to login if not logged in

#     # Get the user's age group from the session
#     age_group = request.session.get('age_group')  # Age group should be stored in session

#     if not age_group:
#         messages.error(request, "Age group not found. Please log in again.")
#         return redirect('user_login')

#     # Store the start time in the session when the test is started
#     if not request.session.get('start_time'):
#         start_time = datetime.now()  # Capture current time
#         request.session['start_time'] = start_time.isoformat()  # Store as a string

#     # Fetch the questions based on the user's age group
#     questions = AgeBasedQuestion.objects.filter(age_group=age_group)

#     if not questions:
#         messages.error(request, f"No questions found for age group: {age_group}")
#         return render(request, 'user/attempt_test.html', {'age_group': age_group})

#     # Store the correct words list in the session for scoring
#     correct_words_list = []
#     for question in questions:
#         correct_words_list.extend(question.words.split(','))  # Split words by commas

#     # Save the correct words list in the session for later comparison during scoring
#     request.session['correct_words_list'] = correct_words_list

#     return render(request, 'user/attempt_test.html', {'questions': questions, 'age_group': age_group, 'correct_words_list': correct_words_list})

def attempt_test(request):
    if not request.session.get('user_id'):
        return redirect('user_login')

    age_group = request.session.get('age_group')
    if not age_group:
        messages.error(request, "Age group not found. Please log in again.")
        return redirect('user_login')

    all_questions = AgeBasedQuestion.objects.filter(age_group=age_group)

    if not all_questions.exists():
        messages.error(request, f"No questions found for age group: {age_group}")
        return render(request, 'user/attempt_test.html', {'age_group': age_group})

    selected_question = None
    current_question_id = request.session.get('current_question_id')

    if current_question_id:
        selected_question = AgeBasedQuestion.objects.filter(
            id=current_question_id,
            age_group=age_group
        ).first()

    if not selected_question:
        questions_list = list(all_questions)
        selected_question = random.choice(questions_list)
        request.session['current_question_id'] = selected_question.id

    # Split words by comma and clean them
    words = [w.strip() for w in selected_question.words.split(',') if w.strip()]

    # Store in session for scoring
    request.session['current_correct_words'] = words

    # Set start time if not already set
    if 'start_time' not in request.session:
        request.session['start_time'] = datetime.now().isoformat()

    return render(request, 'user/attempt_test.html', {
        'questions': [selected_question],
        'age_group': age_group,
    })

from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import json

def submit_word_recall(request):
    """Handle word recall test submission."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Not logged in'}, status=401)
    
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    
    # Get the recalled words from POST data
    recalled_words = request.POST.get('recalled_words', '').strip()
    
    # Get the correct words from session (stored during attempt_test)
    correct_words = request.session.get('current_correct_words', [])
    age_group = request.session.get('age_group', 'Unknown')
    
    # Calculate score based on correctly recalled words
    # Split by commas and clean up
    recalled_list = [word.strip().lower() for word in recalled_words.split(',') if word.strip()]
    correct_words_lower = [word.lower() for word in correct_words]
    
    # Calculate matches (case-insensitive)
    correct_matches = 0
    matched_words = []
    
    for recalled in recalled_list:
        if recalled in correct_words_lower and recalled not in matched_words:
            correct_matches += 1
            matched_words.append(recalled)
    
    # Calculate score (0-20 range)
    total_words = len(correct_words)
    if total_words > 0:
        # Calculate percentage and map to 0-20 scale
        percentage = correct_matches / total_words
        score = int(percentage * 20)  # This gives 0-20 score
    else:
        score = 0

    time_taken = 30  # Default
    if 'start_time' in request.session:
        try:
            start_time = datetime.fromisoformat(request.session['start_time'])
            time_taken = int((datetime.now() - start_time).total_seconds())
        except:
            pass
    
    result = WordRecallResult.objects.create(
        user=user,
        age_group=age_group,
        recalled_words=recalled_words,
        score=score,
        status='Completed',
        time_taken=time_taken
    )
    
    # Clear session data
    request.session.pop('current_correct_words', None)
    request.session.pop('current_question_id', None)
    request.session.pop('start_time', None)
    
    return JsonResponse({
        'success': True,
        'score': score,
        'correct_words': correct_matches,
        'total_words': total_words,
        'result_id': result.id,
        'message': f'You recalled {correct_matches} out of {total_words} words correctly! Your score: {score}/20',
        'max_score': 20,
        'percentage': int((correct_matches / total_words) * 100) if total_words > 0 else 0
    })

def result_page(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = User.objects.get(id=user_id)
    age_group = request.session.get('age_group')

    if request.method == 'POST':
        recalled_words = request.POST.get('recalled_words', '').strip()
        if not recalled_words:
            messages.warning(request, "No words were recalled.")

        # Get correct words from session
        correct_words_list = request.session.get('correct_words_list', [])
        if not correct_words_list:
            messages.error(request, "Test data expired. Please take the test again.")
            return redirect('attempt_test')

        # Scoring logic
        recalled_words_list = [clean_word(w) for w in recalled_words.split() if w.strip()]
        correct_words_cleaned = []
        for phrase in correct_words_list:
            words = [clean_word(w) for w in phrase.split() if w.strip()]
            correct_words_cleaned.extend(words)

        # Use set intersection for unique correct matches
        correct_count = len(set(recalled_words_list) & set(correct_words_cleaned))
        total_words = len(set(correct_words_cleaned))  # avoid counting duplicates in target list

        score = round((correct_count / total_words * 20) if total_words > 0 else 0)

        # Time calculation
        start_time_str = request.session.get('start_time')
        time_taken = 0
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                time_taken = int((datetime.now() - start_time).total_seconds())
            except:
                pass

        # Save result
        result = WordRecallResult(
            user=user,
            age_group=age_group,
            recalled_words=recalled_words,
            score=score,
            time_taken=time_taken,
            status='Completed'
        )
        result.save()

        # Clean up session
        for key in ['start_time', 'correct_words_list']:
            request.session.pop(key, None)

        # Store result ID in session so GET can find the latest result
        request.session['latest_result_id'] = result.id

        # Redirect to GET version of this page
        return redirect('result_page')

    # GET request: Show all results
    results = WordRecallResult.objects.filter(user=user, status='Completed').order_by('-date_attempted')

    context = {
        'results': results,
        'age_group': age_group,
    }

    return render(request, 'user/result_page.html', context)

def word_recall(request):
    if request.method == 'POST':
        age_group = request.POST.get('age_group')
        difficulty = request.POST.get('difficulty')
        words = request.POST.get('words')
        
        if not age_group or not difficulty or not words:
            return render(request, 'admin1/word_recall.html', {'message': 'Please fill in all fields.'})

        # Create a new Age-Based Question
        new_question = AgeBasedQuestion.objects.create(
            age_group=age_group,
            difficulty=difficulty,
            words=words
        )
        return redirect('admin_dashboard')  # Redirect to the dashboard after submission
    
    return render(request, 'admin1/word_recall.html')

def view_questions(request):
    questions = AgeBasedQuestion.objects.all()
    grouped_questions = {}
    for question in questions:
        if question.age_group not in grouped_questions:
            grouped_questions[question.age_group] = {}
        
        if question.difficulty not in grouped_questions[question.age_group]:
            grouped_questions[question.age_group][question.difficulty] = []
        grouped_questions[question.age_group][question.difficulty].append(question)
    return render(request, 'admin1/view_questions.html', {'grouped_questions': grouped_questions})

from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('/')


def verbal_fluency(request):
    if request.method == 'POST':
        fluency_image = request.FILES.get('fluency_image')
        tags = request.POST.get('tags')
        category = request.POST.get('category')
        if fluency_image and tags:
            TestImage.objects.create(fluency_image=fluency_image, tags=tags, category=category)
            messages.success(request, "Image uploaded successfully!")
            return redirect('verbal_fluency')
        messages.error(request, "Please provide both an image and tags.")
    return render(request, 'admin1/verbal_fluency.html')

from django.http import JsonResponse

def attempt_fluency(request):
    user = User.objects.get(id=request.session.get('user_id'))

    def get_next_test_image():
        attempted = FluencyTestResult.objects.filter(user=user)\
                                            .values_list('test_image_id', flat=True)
        remaining_images = TestImage.objects.exclude(id__in=attempted)

        remaining_images = list(remaining_images)
        random.shuffle(remaining_images)

        # Return the first image from the shuffled list
        return remaining_images[0] if remaining_images else None

    test_image = get_next_test_image()

    if not test_image:
        messages.info(request, "You've completed all available fluency images.")
        return render(request, 'user/attempt_fluency.html', {
            'test_image': None,
            'image_url': None,
            'tags': [],
            'already_attempted': False,
            'previous_result': None,
        })

    tags = test_image.get_tags() or []
    unique_tags = list(set(tag.strip() for tag in tags if tag.strip()))
    image_url = test_image.fluency_image.url if test_image.fluency_image else None

    if request.method == 'POST':
        try:
            correct_str = request.POST.get('correct_answers')
            wrong_str   = request.POST.get('wrong_answers')

            if correct_str is None or wrong_str is None:
                raise ValueError("Missing correct_answers or wrong_answers in POST data")

            correct = int(correct_str)
            wrong   = int(wrong_str)

            total = len(unique_tags)
            if total == 0:
                score = 30.0
            else:
                correct = min(correct, total)
                score = 30 + (correct / total) * 30
                score = round(max(30, min(60, score)), 1)

            FluencyTestResult.objects.create(
                user=user,
                test_image=test_image,       
                correct_answers=correct,
                wrong_answers=wrong,
                score=score,
            )

            messages.success(request, f"Score saved: {score:.1f} ({correct} correct, {wrong} wrong)")
            return redirect('attempt_fluency')

        except ValueError as ve:
            messages.error(request, f"Invalid data: {str(ve)}")
        except Exception as e:
            messages.error(request, f"Server error while saving: {str(e)}")

        return render(request, 'user/attempt_fluency.html', {
            'test_image': test_image,
            'image_url': image_url,
            'tags': unique_tags,
            'already_attempted': False,
            'previous_result': None,
        })

    return render(request, 'user/attempt_fluency.html', {
        'test_image': test_image,
        'image_url': image_url,
        'tags': unique_tags,
        'already_attempted': False,
        'previous_result': None,
    })


def check_number_memory_click(request):
    """AJAX: process a click during recall phase."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    try:
        index = int(request.POST.get('index'))
        if index < 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid index'}, status=400)

    grid = request.session.get('memory_grid')
    expected_order = request.session.get('memory_expected_order')   # fixed typo
    next_index = request.session.get('memory_next_index', 0)
    revealed = request.session.get('memory_revealed')
    history = request.session.get('memory_history', [])
    recall_start = request.session.get('memory_start_recall')

    if None in (grid, expected_order, revealed):
        return JsonResponse({'error': 'Test session expired'}, status=400)

    # Ensure recall phase has started
    if recall_start is None:
        return JsonResponse({'error': 'Recall phase not started'}, status=400)

    # If cell already revealed, ignore
    if revealed[index] is not None:
        return JsonResponse({'error': 'Cell already revealed'}, status=400)

    number = grid[index]
    is_correct = (number == expected_order[next_index])

    # Update revealed status
    if is_correct:
        revealed[index] = 'correct'
        next_index += 1
    else:
        revealed[index] = 'wrong'

    # Record click
    history.append({'index': index, 'number': number, 'correct': is_correct})

    # Save back to session
    request.session['memory_next_index'] = next_index
    request.session['memory_revealed'] = revealed
    request.session['memory_history'] = history

    # Check if all cells are revealed (test finished)
    all_revealed = all(r is not None for r in revealed)
    if all_revealed:
        # Calculate time taken from recall start
        time_taken = 0
        if recall_start:
            try:
                start = datetime.fromisoformat(recall_start)
                time_taken = int((datetime.now() - start).total_seconds())
            except Exception:
                pass

        # Calculate score based on correct clicks (range 30-120)
        total_cells = len(grid)
        correct_count = next_index  # because next_index counts correct clicks
        
        # Score calculation: map correct_clicks (0 to total_cells) to 30-120 range
        if total_cells > 0:
            # Linear mapping: 0 correct = 30, total_cells correct = 120
            score = 30 + int((correct_count / total_cells) * 90)
        else:
            score = 30
        
        # Ensure score stays within bounds
        score = max(30, min(120, score))

        # Get user and config
        user = User.objects.get(id=user_id)
        config_id = request.session.get('memory_config_id')
        config = None
        if config_id:
            try:
                config = NumberMemoryConfig.objects.get(id=config_id)
            except NumberMemoryConfig.DoesNotExist:
                pass

        # Save result to database with score
        NumberMemoryResult.objects.create(
            user=user,
            config=config,
            grid=grid,
            click_history=history,
            correct_clicks=correct_count,   # because next_index counts correct clicks
            mistakes=len(history) - correct_count,
            time_taken=time_taken,
            score=score  # Add the calculated score
        )

        # Clear session data for this test
        keys = ['memory_config_id', 'memory_grid', 'memory_expected_order',
                'memory_next_index', 'memory_revealed', 'memory_history',
                'memory_start_recall']
        for key in keys:
            request.session.pop(key, None)

        return JsonResponse({
            'status': 'completed',
            'correct': is_correct,
            'number': number,
            'next_expected': expected_order[next_index] if next_index < len(expected_order) else None,
            'all_revealed': True,
            'score': score  # Include score in response if needed
        })


    return JsonResponse({
        'status': 'success',
        'correct': is_correct,
        'number': number,
        'next_expected': expected_order[next_index] if next_index < len(expected_order) else None,
        'all_revealed': False
    })

def number_memory_config(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        difficulty = request.POST.get('difficulty')
        grid_size = int(request.POST.get('grid_size', 3))
        start = int(request.POST.get('number_range_start', 1))
        end = int(request.POST.get('number_range_end', 9))

        # Validate that the range contains exactly grid_size² numbers
        if (end - start + 1) != grid_size * grid_size:
            messages.error(request, f"Range must contain exactly {grid_size*grid_size} numbers.")
        else:
            NumberMemoryConfig.objects.create(
                name=name,
                difficulty=difficulty,
                grid_size=grid_size,
                number_range_start=start,
                number_range_end=end,
                is_active=True
            )
            messages.success(request, "Configuration added successfully.")
            return redirect('number_memory_config')

    configs = NumberMemoryConfig.objects.all().order_by('-id')
    return render(request, 'admin1/number_memory_config.html', {'configs': configs})

def admin_number_memory_results(request):
    """Show all Number Memory test results for admin."""
    if not request.session.get('admin_name'):
        return redirect('admin_login')

    results = NumberMemoryResult.objects.select_related('user', 'config').order_by('-date_attempted')
    return render(request, 'admin1/number_memory_results.html', {'results': results})

def start_number_memory_test(request):
    if not request.session.get('user_id'):
        return redirect('user_login')

    # Retrieve user's age (defaulting to 30 if not found in session)
    user_age = request.session.get('user_age', 30)

    # Set grid size and difficulty based on the user's age
    if user_age < 30:
        grid_size = 5  # Hard: 5x5 grid for young users
        difficulty = 'hard'
    elif 30 <= user_age <= 60:
        grid_size = 4  # Medium: 4x4 grid for middle-aged users
        difficulty = 'medium'
    else:
        grid_size = 3  # Easy: 3x3 grid for senior users
        difficulty = 'easy'

    # Store the grid size and difficulty in the session for future requests
    request.session['memory_grid_size'] = grid_size
    request.session['memory_difficulty'] = difficulty

    # Calculate the total number of cells based on grid_size (e.g., 5x5, 4x4, 3x3)
    total_cells = grid_size * grid_size

    # Generate random numbers for the grid based on the config
    numbers = list(range(1, total_cells + 1))  # Numbers from 1 to total_cells

    # Shuffle the numbers based on the user's age group (not the grid size)
    random.shuffle(numbers)

    # Store the session values to keep track of the test state
    request.session['memory_grid'] = numbers  # Shuffle the numbers, not the grid itself
    request.session['memory_next'] = numbers[0]
    request.session['memory_expected_order'] = sorted(numbers)
    request.session['memory_next_index'] = 0
    request.session['memory_revealed'] = [None] * len(numbers)
    request.session['memory_history'] = []
    request.session['memory_start_recall'] = None

    # Return the grid for rendering (pass only the required variables to the template)
    return render(request, 'user/number_memory_test.html', {
        'grid': numbers,
        'grid_size': grid_size,
        'difficulty': difficulty,
        'user_age': user_age  # Pass the age for reference in the template
    })

# def start_number_memory_test(request):
#     if not request.session.get('user_id'):
#         return redirect('user_login')

#     # Get user's age from session (you need to store this during login)
#     user_age = request.session.get('user_age', 30)  # Default to 30 if not set
    
#     # Determine grid size based on age
#     if user_age < 30:
#         grid_size = 5  # Hard: 5x5 grid for young users
#         difficulty = 'hard'
#     elif 30 <= user_age <= 60:
#         grid_size = 4  # Medium: 4x4 grid for middle-aged users
#         difficulty = 'medium'
#     else:
#         grid_size = 3  # Easy: 3x3 grid for senior users
#         difficulty = 'easy'
    
#     # Find an active config with the appropriate grid size and difficulty
#     config = NumberMemoryConfig.objects.filter(
#         is_active=True, 
#         grid_size=grid_size,
#         difficulty=difficulty
#     ).order_by('?').first()
    
#     # If no exact match found, try to find any config with the right grid size
#     if not config:
#         config = NumberMemoryConfig.objects.filter(
#             is_active=True, 
#             grid_size=grid_size
#         ).order_by('?').first()
    
#     # If still no config, fall back to any active config
#     if not config:
#         config = NumberMemoryConfig.objects.filter(is_active=True).order_by('?').first()
    
#     if not config:
#         messages.error(request, "No test configurations available. Please contact admin.")
#         return redirect('user_dashboard')

#     numbers = list(range(config.number_range_start, config.number_range_end + 1))
#     random.shuffle(numbers)

#     request.session['memory_config_id'] = config.id
#     request.session['memory_grid'] = numbers
#     request.session['memory_next'] = numbers[0]
#     request.session['memory_expected_order'] = sorted(numbers)
#     request.session['memory_next_index'] = 0
#     request.session['memory_revealed'] = [None] * len(numbers)
#     request.session['memory_history'] = []
#     request.session['memory_start_recall'] = None

#     return render(request, 'user/number_memory_test.html', {
#         'grid': numbers,
#         'grid_size': config.grid_size,
#         'difficulty': config.difficulty,
#         'user_age': user_age
#     })
# # 

def number_memory_results(request):
    """Show past results for the logged-in user."""
    if not request.session.get('user_id'):
        return redirect('user_login')

    user = User.objects.get(id=request.session['user_id'])
    results = NumberMemoryResult.objects.filter(user=user).order_by('-date_attempted')
    return render(request, 'user/number_memory_results.html', {'results': results})

def record_recall_start(request):
    if request.method == 'POST' and request.session.get('user_id'):
        request.session['memory_start_recall'] = datetime.now().isoformat()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid'}, status=400)



def all_scores(request):
    if not request.session.get('user_id'):
        return redirect('user_login')

    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    number_memory_results = NumberMemoryResult.objects.filter(user=user).order_by('-date_attempted')
    word_recall_results = WordRecallResult.objects.filter(user=user).order_by('-date_attempted')
    fluency_results = FluencyTestResult.objects.filter(user=user).select_related('test_image').order_by('-date_attempted')

    number_memory_scores = []
    for result in number_memory_results:
        number_memory_scores.append({
            'exam_type': 'Number Memory',
            'date': result.date_attempted,
            'score': result.score,
            'details': f"{result.correct_clicks} correct, {result.mistakes} mistakes",
            'time_taken': result.time_taken,
            'id': result.id,
            'type': 'number'
        })

    word_recall_scores = []
    for result in word_recall_results:
        word_recall_scores.append({
            'exam_type': 'Word Recall',
            'date': result.date_attempted,
            'score': result.score,
            'details': f"Age Group: {result.age_group}, Status: {result.status}",
            'words_recalled': result.recalled_words,
            'time_taken': result.time_taken,
            'id': result.id,
            'type': 'word'
        })

    fluency_scores = []
    for result in fluency_results:
        score_item = {
            'exam_type': 'Fluency Test',
            'score': result.score,
            'details': f"{result.correct_answers} correct, {result.wrong_answers} wrong",
            'image': result.test_image,
            'id': result.id,
            'type': 'fluency',
            'time_taken': getattr(result, 'time_taken', 0),
            'date': result.date_attempted
        }
        fluency_scores.append(score_item)

    # Get latest scores safely
    number_score = number_memory_results.first().score if number_memory_results.exists() else 0
    word_score = word_recall_results.first().score if word_recall_results.exists() else 0
    fluency_score = fluency_results.first().score if fluency_results.exists() else 0

    # Calculate overall risk score
    risk_score = round((number_score + word_score + fluency_score) / 3, 2)

    context = {
        'user': user,
        'number_memory_scores': number_memory_scores,
        'word_recall_scores': word_recall_scores,
        'fluency_scores': fluency_scores,
        'number_memory_count': number_memory_results.count(),
        'word_recall_count': word_recall_results.count(),
        'fluency_count': fluency_results.count(),
        'risk_score': risk_score
    }

    return render(request, 'user/all_scores.html', context)

def test_scores(request):
    users = User.objects.all()
    test_scores = []

    for user in users:
        number_memory_results = NumberMemoryResult.objects.filter(user=user)
        word_recall_results = WordRecallResult.objects.filter(user=user)
        fluency_results = FluencyTestResult.objects.filter(user=user)

        for result in number_memory_results:
            test_scores.append({
                'username': user.username,
                'test_name': 'Number Memory',
                'score': result.score
            })

        for result in word_recall_results:
            test_scores.append({
                'username': user.username,
                'test_name': 'Word Recall',
                'score': result.score
            })

        for result in fluency_results:
            test_scores.append({
                'username': user.username,
                'test_name': 'Fluency Test',
                'score': result.score
            })

    return render(request, 'admin/test_scores.html', {'test_scores': test_scores})
def user_exam_detail(request, exam_type, result_id):
    """View to show detailed information for a specific exam result."""
    if not request.session.get('user_id'):
        return redirect('user_login')
    
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    
    context = {
        'exam_type': exam_type,
        'result_id': result_id,
    }
    
    if exam_type == 'number':
        # Number Memory Result Details
        result = NumberMemoryResult.objects.filter(
            id=result_id,
            user_id=user_id
        ).select_related('config').first()
        
        if not result:
            messages.error(request, "Number Memory result not found.")
            return redirect('all_scores')
        
        # Calculate accuracy
        total_clicks = result.correct_clicks + result.mistakes
        accuracy = (result.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
        
        # Process grid data
        grid_data = result.grid
        grid_size = int(len(grid_data) ** 0.5)  # Assuming square grid
        
        # Process click history
        click_history = result.click_history
        
        context.update({
            'result': result,
            'grid_data': grid_data,
            'grid_size': grid_size,
            'click_history': click_history,
            'accuracy': round(accuracy, 1),
            'total_clicks': total_clicks,
            'config_name': result.config.name if result.config else 'Standard',
            'difficulty': result.config.difficulty if result.config else 'N/A',
        })
        
        template = 'user/exam_detail_number.html'
        
    elif exam_type == 'word':
        # Word Recall Result Details
        result = WordRecallResult.objects.filter(
            id=result_id,
            user_id=user_id
        ).first()
        
        if not result:
            messages.error(request, "Word Recall result not found.")
            return redirect('all_scores')
        
        # Process words
        recalled_words = result.recalled_words.split(',') if result.recalled_words else []
        recalled_words = [w.strip() for w in recalled_words if w.strip()]
        
        # Get original words from session or result
        # You might want to store original words in the model
        original_words = request.session.get('current_correct_words', [])
        
        # If not in session, try to reconstruct from question bank
        if not original_words and hasattr(result, 'question'):
            original_words = result.question.words.split(',') if result.question else []
        
        # Calculate matches
        correct_matches = 0
        matched_words = []
        missed_words = []
        
        for word in original_words:
            word_lower = word.lower()
            if any(word_lower == recalled.lower() for recalled in recalled_words):
                correct_matches += 1
                matched_words.append(word)
            else:
                missed_words.append(word)
        
        # Find incorrect recalls
        incorrect_recalls = [w for w in recalled_words if w.lower() not in [o.lower() for o in original_words]]
        
        context.update({
            'result': result,
            'original_words': original_words,
            'recalled_words': recalled_words,
            'matched_words': matched_words,
            'missed_words': missed_words,
            'incorrect_recalls': incorrect_recalls,
            'correct_matches': correct_matches,
            'total_words': len(original_words),
            'accuracy': round((correct_matches / len(original_words) * 100), 1) if original_words else 0,
        })
        
        template = 'user/exam_detail_word.html'
        
    elif exam_type == 'fluency':
        # Fluency Test Result Details
        result = FluencyTestResult.objects.filter(
            id=result_id,
            user_id=user_id
        ).select_related('test_image').first()
        
        if not result:
            messages.error(request, "Fluency Test result not found.")
            return redirect('all_scores')
        
        # Calculate statistics
        total_answers = result.correct_answers + result.wrong_answers
        accuracy = (result.correct_answers / total_answers * 100) if total_answers > 0 else 0
        
        context.update({
            'result': result,
            'total_answers': total_answers,
            'accuracy': round(accuracy, 1),
            'image_title': result.test_image,
            'image_category': result.test_image.category if result.test_image else 'N/A',
        })
        
        template = 'user/exam_detail_fluency.html'
    
    else:
        messages.error(request, "Invalid exam type.")
        return redirect('all_scores')
    
    return render(request, template, context)

def exam_detail_word(request, result_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    result = get_object_or_404(WordRecallResult, id=result_id, user=user)
    if result.original_words:
        original_words = [word.strip() for word in result.original_words.split(',') if word.strip()]
    else:
        original_words = []
    if result.recalled_words:
        recalled_words = [word.strip().lower() for word in result.recalled_words.split(',') if word.strip()]
    else:
        recalled_words = []
    original_words_lower = [word.lower() for word in original_words]

    matched_words = []
    for word in recalled_words:
        if word in original_words_lower:
            matched_words.append(word)
    
    # Find missed words
    missed_words = []
    for word in original_words_lower:
        if word not in recalled_words:
            missed_words.append(word)
    incorrect_recalls = []
    for word in recalled_words:
        if word not in original_words_lower:
            incorrect_recalls.append(word)
    correct_matches = len(matched_words)
    if len(original_words) > 0:
        accuracy = (correct_matches / len(original_words)) * 100
    else:
        accuracy = 0
    
    context = {
        'result': result,
        'original_words': original_words,
        'recalled_words': recalled_words,
        'matched_words': matched_words,
        'missed_words': missed_words,
        'incorrect_recalls': incorrect_recalls,
        'correct_matches': correct_matches,
        'accuracy': round(accuracy, 1),
    }
    
    return render(request, 'user/exam_detail_word.html', context)

def exam_detail_number(request, result_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    result = get_object_or_404(NumberMemoryResult, id=result_id, user=user)
    context = {
        'result': result,
        'score': result.score,
        'accuracy': result.accuracy if hasattr(result, 'accuracy') else 0,
        'user':user,
    }
    
    return render(request, 'user/exam_detail_number.html', context)



def exam_detail_fluency(request, result_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    result = get_object_or_404(FluencyTestResult, id=result_id, user=user)
    test_image = result.test_image

    image_url = test_image.fluency_image.url if test_image.fluency_image else None

    context = {
        'result': result,
        'user': user,
        'test_image': test_image,
        'image_url': image_url,
        'image_category': test_image.category if test_image else '',
        'original_words': test_image.get_tags() if test_image else [],
        'recalled_words': result.recalled_words if hasattr(result, 'recalled_words') else [],
        'correct_words': result.correct_words if hasattr(result, 'correct_words') else [],
        'incorrect_words': result.incorrect_words if hasattr(result, 'incorrect_words') else [],
        'missed_words': result.missed_words if hasattr(result, 'missed_words') else [],
        'total_words': result.correct_answers + result.wrong_answers,
    }
    
    return render(request, 'user/exam_detail_fluency.html', context)


def user_profile(request):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    return render(request,'user/user_profile.html',{'user':user})