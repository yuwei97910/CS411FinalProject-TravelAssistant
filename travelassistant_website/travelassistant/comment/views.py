from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm, CommentBoxSearchForm
from django.http import Http404 #handle missing object
from django.db import connections
from django.db import connection

from trip.models import (
    Accommodations,
    Attractions,
    City,
    Laundry,
    Markets,
    Restaurants,
)
# from trip.views import spot_list
from comment.models import (
    delete_comment_by_id,
    get_all_comment,
    AccommodationsComments,
    AttractionsComments,
    RestaurantsComments
)
from accounts.models import (
    Users,
    Preference
)

def spot_list(spot, keyword):
    # with connections['travel_db'].cursor() as cursor:
    with connections['default'].cursor() as cursor:
        if spot.lower() == 'restaurants':
            query = "SELECT * FROM restaurants_comments JOIN restaurants USING(restaurant_id) where r_name like '%{k}%';".format(
                 k=keyword)
        elif spot.lower() == 'accommodations':
            query = "SELECT * FROM accommodations_comments JOIN accommodations USING(accommodation_id) where ac_name like '%{k}%';".format(
                 k=keyword)
        elif spot.lower() == 'attractions':
            query = "SELECT * FROM attractions_comments JOIN attractions USING(attraction_id) where a_name like '%{k}%';".format(
                 k=keyword)
        cursor.execute(query)
        c = cursor.fetchall()
    return c

def comment_detail(request):
    if request.method == "POST":
        if request.POST['submit'] == "Search":
            form_result = CommentBoxSearchForm(request.POST)
            if form_result.is_valid():
                query_result = spot_list(
                    form_result.cleaned_data['spot'], form_result.cleaned_data['keyword'])
                result_list = []
                if form_result.cleaned_data['spot'] == 'Restaurants':
                    result_list = [{'rating':item[4], 'comment': item[5], 'name': item[7],
                                    'type': form_result.cleaned_data['spot']} for item in query_result]
                elif form_result.cleaned_data['spot'] == 'Accommodations':
                    result_list = [{'rating':item[4], 'comment': item[5], 'name': item[7],
                                    'type': form_result.cleaned_data['spot']} for item in query_result]
                elif form_result.cleaned_data['spot'] == 'Attractions':
                    result_list = [{'rating':item[4], 'comment': item[5], 'name': item[9],
                                    'type': form_result.cleaned_data['spot']} for item in query_result]
                with connections['default'].cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE user_id=%s",[request.session['user_id']])
                    superstar = cursor.fetchall()[0]

                user_id = request.session['user_id']
                restaurant_comment_list = get_all_comment('restaurants_comments', user_id)
                restaurant_comment_result = [ {'restaurant_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'r_name':item[7], 'like':item[6]} for item in restaurant_comment_list]
                attractions_comment_list = get_all_comment('attractions_comments', user_id)
                attractions_comment_result = [ {'attraction_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'a_name':item[7], 'like':item[6]} for item in attractions_comment_list]
                accommodations_comment_list = get_all_comment('accommodations_comments', user_id)
                accommodations_comment_result = [ {'accommodation_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'ac_name':item[7], 'like':item[6]} for item in accommodations_comment_list]
                comment_search_box_form = CommentBoxSearchForm()
                comment_name = form_result.cleaned_data['keyword']
                context = {
                    # 'trip_search_box_form': TripSearchBoxForm(),
                    'comment_name':comment_name,
                    'trip_search_box_form': form_result,
                    'form_result': form_result,
                    'result_list': result_list,
                    'restaurant_comment_result': restaurant_comment_result,
                    'attractions_comment_result': attractions_comment_result,
                    'accommodations_comment_result': accommodations_comment_result,
                    'user_id': user_id,
                    'comment_search_box_form' : comment_search_box_form,
                    'superstar':superstar[9],
                }
                # return render(request, 'comment_detail_allcomments.html', context)
                return render(request, 'comment_detail.html', context)
            else:
                print(form_result.errors)

    with connections['default'].cursor() as cursor:
        cursor.execute("select * from users where user_id=%s",[request.session['user_id']])
        superstar = cursor.fetchall()[0]

    user_id = request.session['user_id']
    restaurant_comment_list = get_all_comment('restaurants_comments', user_id)
    restaurant_comment_result = [ {'restaurant_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'r_name':item[7], 'like':item[6]} for item in restaurant_comment_list]
    attractions_comment_list = get_all_comment('attractions_comments', user_id)
    attractions_comment_result = [ {'attraction_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'a_name':item[7], 'like':item[6]} for item in attractions_comment_list]
    accommodations_comment_list = get_all_comment('accommodations_comments', user_id)
    accommodations_comment_result = [ {'accommodation_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'ac_name':item[7], 'like':item[6]} for item in accommodations_comment_list]
    comment_search_box_form = CommentBoxSearchForm()

    context = {
        'restaurant_comment_result': restaurant_comment_result,
        'attractions_comment_result': attractions_comment_result,
        'accommodations_comment_result': accommodations_comment_result,
        'user_id': user_id,
        'comment_search_box_form' : comment_search_box_form,
        'superstar':superstar[9],
    }
    return render(request, 'comment_detail.html', context)

def comment_delete(request, comment_id):
    if request.method == "POST":
        user_id = request.session['user_id']

        if request.POST['submit'] == "Delete Restaurants Comment":
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM restaurants_comments WHERE comment_id=%s",[comment_id])
        elif request.POST['submit'] == "Delete Accommodations Comment":
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM accommodations_comments WHERE comment_id=%s",[comment_id])
        elif request.POST['submit'] == "Delete Attractions Comment":
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM attractions_comments WHERE comment_id=%s",[comment_id])
        # writr update user to activate trigger
        with connection.cursor() as cursor:
            query = """
            UPDATE users SET superstar = False WHERE user_id = '{}';
            """.format(request.session['user_id'])
            cursor.execute(query)

            cursor.execute("select * from users where user_id=%s",[request.session['user_id']])
            superstar = cursor.fetchall()[0]

        comment_search_box_form = CommentBoxSearchForm()
        restaurant_comment_list = get_all_comment('restaurants_comments', user_id)
        restaurant_comment_result = [ {'restaurant_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'r_name':item[7], 'like':item[6]} for item in restaurant_comment_list]
        attractions_comment_list = get_all_comment('attractions_comments', user_id)
        attractions_comment_result = [ {'attraction_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'a_name':item[7], 'like':item[6]} for item in attractions_comment_list]
        accommodations_comment_list = get_all_comment('accommodations_comments', user_id)
        accommodations_comment_result = [ {'accommodation_id':item[0],'comment_id': item[1], 'user_id': item[2], 'date':item[3],'comment':item[5],'ac_name':item[7], 'like':item[6]} for item in accommodations_comment_list]
        context = {
            'restaurant_comment_result': restaurant_comment_result,
            'attractions_comment_result': attractions_comment_result,
            'accommodations_comment_result': accommodations_comment_result,
            'comment_search_box_form' : comment_search_box_form,
            'user_id': user_id,
            'superstar':superstar[9],
        }
        # return render(request, 'comment_detail.html', context)
        return redirect('/comment/comment_detail')


def comment_edit(request, comment_id):

    if request.method == "POST":
        user_id = request.session['user_id']
        if request.POST['submit'] == "Edit Restaurants Comment":
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM restaurants_comments WHERE comment_id = %s;" % comment_id)
                r_comment = cursor.fetchall()[0]

            obj = Restaurants.objects.get(restaurant_id=r_comment[2])
            initial_value = {'comment': r_comment[5],
                    # 'comment_date':r_comment[3],
                    'rating_score': r_comment[4]
            }
            edit_type = 'restaurants_comments'

        elif request.POST['submit'] == "Edit Accommodations Comment":
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM accommodations_comments WHERE comment_id = %s;" % comment_id)
                r_comment = cursor.fetchall()[0]

            obj = Accommodations.objects.get(accommodation_id=r_comment[2])
            initial_value = {'comment': r_comment[5],
                    # 'comment_date':r_comment[3],
                    'rating_score': r_comment[4]
            }
            edit_type = 'accommodations_comments'


        elif request.POST['submit'] == "Edit Attractions Comment":
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM attractions_comments WHERE comment_id = %s;" % comment_id)
                r_comment = cursor.fetchall()[0]

            obj = Attractions.objects.get(attraction_id=r_comment[2])
            initial_value = {'comment': r_comment[5],
                    'rating_score': r_comment[4]
            }
            edit_type = 'attractions_comments'


        target_form = CommentForm(initial=initial_value)
        context = {
            'comment_id': comment_id,
            'edit_type': edit_type,
            'comment_form': target_form,
            'object': obj
        }
        return render(request, 'comment_edit.html', context)

    comment_form = CommentForm()
    context = {
        'comment_form': comment_form,
    }
    return render(request, 'comment_edit.html', context)

def comment_update(request, comment_id):

    if request.method == "POST":
        if request.POST['comment_button'] == "Update Restaurants Comment":
            update_form = CommentForm(request.POST)
            if update_form.is_valid():
                input_comment_date = update_form.cleaned_data['comment_date']
                input_comment = update_form.cleaned_data['comment']
                input_comment_rating = update_form.cleaned_data['rating_score']
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE restaurants_comments SET comment_date = %s, comment = %s, rating = %s WHERE comment_id = %s;""",
                        [input_comment_date, input_comment, input_comment_rating, comment_id])

        elif request.POST['comment_button'] == "Update Accommodations Comment":
            update_form = CommentForm(request.POST)
            if update_form.is_valid():
                input_comment_date = update_form.cleaned_data['comment_date']
                input_comment = update_form.cleaned_data['comment']
                input_comment_rating = update_form.cleaned_data['rating_score']
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE accommodations_comments SET comment_date = %s, comment = %s, rating = %s WHERE comment_id = %s;""",
                        [input_comment_date, input_comment, input_comment_rating, comment_id])

        elif request.POST['comment_button'] == "Update Attractions Comment":
            update_form = CommentForm(request.POST)
            if update_form.is_valid():
                input_comment_date = update_form.cleaned_data['comment_date']
                input_comment = update_form.cleaned_data['comment']
                input_comment_rating = update_form.cleaned_data['rating_score']
                with connection.cursor() as cursor:
                    cursor.execute("""UPDATE attractions_comments SET comment_date = %s, comment = %s, rating = %s WHERE comment_id = %s;""",
                        [input_comment_date, input_comment, input_comment_rating, comment_id])

    form=CommentForm()
    return redirect('/comment/comment_detail')
