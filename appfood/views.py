from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
# Login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import CommentForm


# Create your views here.


# Login-Out-------------
def logoutPage(request):
    logout(request)
    return redirect('viewhome')


def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  # Kiểm tra nếu người dùng là admin
            return redirect('ad')  # Điều hướng đến trang admin
        else:
            return redirect('home')  # Điều hướng đến trang chủ người dùng

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:  # Nếu người dùng là admin
                return redirect('ad')  # Điều hướng đến trang admin
            else:
                return redirect('home')  # Điều hướng đến trang chủ người dùng
        else:
            messages.info(request, 'Tài Khoản Đăng Nhập Chưa Đúng..!')

    context = {}
    return render(request, 'appfood/login.html', context)


# Đăng Ký
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username).exists():
            error = "Tên đăng nhập đã tồn tại."
            return render(request, 'appfood/register.html', {'error': error})

        if User.objects.filter(email=email).exists():
            error = "Email đã tồn tại."
            return render(request, 'appfood/register.html', {'error': error})

        if password1 == password2:
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name,
                                            last_name=last_name)
            user.save()
            login(request, user)
            return redirect('home')
        else:
            error = "Mật khẩu không trùng khớp."
            return render(request, 'appfood/register.html', {'error': error})
    return render(request, 'appfood/register.html')


# User-------------------------------------------------------
# @login_required
# def home(request):
#     recipes = Recipe.objects.all()
#     recipeimage = RecipeImage.objects.all()
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#     return render(request,'appfood/home.html', {'recipes': recipes,'recipeimage':recipeimage,'user_profile': user_profile},)

@login_required
def home(request):
    # Lấy tất cả sảnphẩm và thêm các mối quan hệ liên quan để tối ưu hóa truy vấn
    recipes = Recipe.objects.all().select_related('author', 'author__userprofile').prefetch_related('images',
                                                                                                    'classify')
    # Lấy 5 sản phẩm có lượt xem cao nhất
    top_recipes = Recipe.objects.all().order_by('-views')[:5]
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    recipeimage = RecipeImage.objects.all()
    unread_notifications_count = Notification.objects.filter(recipient=request.user, read=False).count()

    return render(request, 'appfood/home.html', {
        'recipes': recipes,
        'top_recipes': top_recipes,
        'recipeimage': recipeimage,
        'user_profile': user_profile,
        'unread_notifications_count': unread_notifications_count,
    })


# Repost----------------------------------------------------
@login_required
def report_food(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.reported = True
    recipe.save()
    messages.success(request, 'Tố cáo bài viết thành công.')
    return redirect('home')


# Detail----------------------------------------

@login_required
def detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    is_following = Follow.objects.filter(follower=request.user, followed=recipe.author).exists()
    recipe.views += 1  # Tăng số lượt xem lên 1
    recipe.save()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            if parent_id:  # Nếu có parent_id, đây là một reply
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()

            # Tạo thông báo cho tác giả của bài viết
            if recipe.author != request.user:
                Notification.objects.create(
                    recipient=recipe.author,
                    sender=request.user,
                    recipess=recipe,
                    message=f'{request.user.last_name} {request.user.first_name} đã bình luận về bài viết của bạn.',
                    read=False
                )

            return redirect('detail', recipe_id=recipe_id)
    else:
        form = CommentForm()

    comments = recipe.comments.filter(parent__isnull=True)  # Chỉ hiển thị bình luận gốc, không phải reply
    images = RecipeImage.objects.filter(recipe=recipe)  # Lấy tất cả ảnh của công thức này
    total_count = comments.count() + Comment.objects.filter(parent__in=comments).count()
    author_profile = get_object_or_404(UserProfile, user=recipe.author)
    is_own_recipe = recipe.author == request.user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'appfood/detail.html',
                  {'recipe': recipe,
                   'images': images,
                   'comments': comments,
                   'form': form,
                   'total_count': total_count,
                   'is_following': is_following,
                   'is_own_recipe': is_own_recipe,
                   'author_profile': author_profile,
                   'user_profile': user_profile})


# Admin----------------------------------------------------
@login_required
def home_admin(request):
    recipes = Recipe.objects.all()
    recipeimage = RecipeImage.objects.all()
    return render(request, 'admin/home_admin.html', {'recipes': recipes, 'recipeimage': recipeimage})


@login_required
def admin_delete(request, post_id):
    if request.user.is_staff:
        post = get_object_or_404(Recipe, id=post_id)
        post.delete()
        messages.success(request, 'Đã xoá bài post thành công.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def rpfood(request):
    recipes = Recipe.objects.filter(reported=True)
    recipeimage = RecipeImage.objects.all()
    return render(request, 'admin/rpfood.html', {'recipes': recipes, 'recipeimage': recipeimage})


@login_required
def detail_admin(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    images = RecipeImage.objects.filter(recipe=recipe)  # Lấy tất cả ảnh của công thức này

    return render(request, 'admin/detail_admin.html',
                  {'recipe': recipe,
                   'images': images,
                   'recipe': recipe,
                   })


# View----------------------------------------------------
def viewhome(request):
    recipes = Recipe.objects.all()
    recipeimage = RecipeImage.objects.all()
    return render(request, 'view/viewhome.html', {'recipes': recipes, 'recipeimage': recipeimage})


# Like -------------------------------------------------------------------------------------------
@login_required
def savefood(request):
    if request.user.is_authenticated:
        liked_recipes = request.user.liked_recipes.all()  # Lấy danh sách công thức người dùng đã thích
        recipes = Recipe.objects.all()
        recipeimage = RecipeImage.objects.all()
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        return render(request, 'appfood/savefood.html',
                      {'liked_recipes': liked_recipes, 'recipes': recipes, 'recipeimage': recipeimage,
                       'user_profile': user_profile})
    return redirect('login')  # Yêu cầu đăng nhập nếu chưa đăng nhập


# @login_required
# def like_recipe(request, recipe_id):
#     recipe = get_object_or_404(Recipe, id=recipe_id)
#     if request.user in recipe.liked_tym.all():
#         recipe.liked_tym.remove(request.user)  # Xóa người dùng khỏi danh sách yêu thích
#         messages.success(request, 'Bạn đã bỏ thích bài viết.')
#     else:
#         recipe.liked_tym.add(request.user)  # Thêm người dùng vào danh sách yêu thích
#         messages.success(request, 'Bạn đã thích bài viết.')

#         # Tạo thông báo cho tác giả của bài viết
#         if recipe.author != request.user:
#             Notification.objects.create(
#                 recipient=recipe.author,
#                 sender=request.user,
#                 recipess=recipe,
#                 message=f'{request.user.last_name} {request.user.first_name} đã thích bài viết của bạn.',
#                 read=False
#             )
#     return redirect(request.META.get('HTTP_REFERER', 'home'))  # Quay lại trang hiện tại


@login_required
def like_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    liked = False
    if request.user in recipe.liked_tym.all():
        recipe.liked_tym.remove(request.user)  # Xóa người dùng khỏi danh sách yêu thích
        messages.success(request, 'Bạn đã bỏ thích bài viết.')
    else:
        recipe.liked_tym.add(request.user)  # Thêm người dùng vào danh sách yêu thích
        messages.success(request, 'Bạn đã thích bài viết.')
        liked = True

        # Tạo thông báo cho tác giả của bài viết
        if recipe.author != request.user:
            Notification.objects.create(
                recipient=recipe.author,
                sender=request.user,
                recipess=recipe,
                message=f'{request.user.last_name} {request.user.first_name} đã thích bài viết của bạn.',
                read=False
            )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'total_likes': recipe.total_likes()})

    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Quay lại trang hiện tại


# My Food------------------------------------------------------------------------------------------------------------------------

@login_required
def myfood(request):
    recipes = Recipe.objects.filter(author=request.user)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'appfood/myfood.html', {'recipes': recipes, 'user_profile': user_profile})


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    recipe.delete()
    return redirect('myfood')


@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    images = RecipeImage.objects.filter(recipe=recipe)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        # Cập nhật thông tin công thức
        title = request.POST.get("title")
        introduce = request.POST.get("introduce")
        description = request.POST.get("description")
        recipe.title = title
        recipe.introduce = introduce
        recipe.description = description

        # Xử lý việc lưu phân loại
        classify_names = request.POST.getlist('classify')  # Lấy danh sách tên phân loại từ form
        classify_ids = []

        for name in classify_names:
            classify, created = Classify.objects.get_or_create(name=name)
            classify_ids.append(classify.id)

        recipe.classify.set(classify_ids)  # Sử dụng phương thức set() để cập nhật Many-to-Many

        recipe.save()

        # Xử lý việc tải lên nhiều ảnh
        image_files = request.FILES.getlist('images')
        if image_files:
            for image_file in image_files:
                RecipeImage.objects.create(recipe=recipe, image=image_file)

        # Xóa ảnh đã chọn
        delete_image_ids = request.POST.getlist('delete_images')
        if delete_image_ids:
            RecipeImage.objects.filter(id__in=delete_image_ids, recipe=recipe).delete()

        return redirect('myfood')  # Điều hướng tới trang mong muốn

    return render(request, 'appfood/edit.html', {'recipe': recipe, 'images': images, 'user_profile': user_profile})


# Tìm Kiếm -------------------------------------------------------------------------
@login_required
def search_title(request):
    searched = None
    checks = None
    if request.method == 'POST':
        searched = request.POST['searched']
        checks = Recipe.objects.filter(title__contains=searched).select_related('author', 'author__userprofile')
    recipe = Recipe.objects.all()
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'appfood/search_title.html',
                  {'recipe': recipe, 'searched': searched, 'checks': checks, 'user_profile': user_profile})


# Filter food---------------------------------------------------------------------------------------------------------------
# Chay
@login_required
def vegetarian(request):
    # Tìm phân loại "Món Chay"
    vegetarian_class = Classify.objects.get(name='Chay')
    # Lấy tất cả các công thức nấu ăn thuộc phân loại "Món Chay"
    vegetarian_recipes = Recipe.objects.filter(classify=vegetarian_class).select_related('author',
                                                                                         'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/vegetarian.html', {'recipes': vegetarian_recipes, 'user_profile': user_profile})


# Vặt
@login_required
def grill(request):
    grill_class = Classify.objects.get(name='Nướng')
    grill_recipes = Recipe.objects.filter(classify=grill_class).select_related('author', 'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/grill.html', {'recipes': grill_recipes})


# Món Á
@login_required
def asian(request):
    asian_class = Classify.objects.get(name='Món Á')
    asian_recipes = Recipe.objects.filter(classify=asian_class).select_related('author', 'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/asian.html', {'recipes': asian_recipes, 'user_profile': user_profile})


# Món Âu
@login_required
def european(request):
    european_class = Classify.objects.get(name='Món Âu')
    european_recipes = Recipe.objects.filter(classify=european_class).select_related('author', 'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/european.html', {'recipes': european_recipes, 'user_profile': user_profile})


# Khai Vị
@login_required
def appetizer(request):
    appetizer_class = Classify.objects.get(name='Khai Vị')
    appetizer_recipes = Recipe.objects.filter(classify=appetizer_class).select_related('author', 'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/appetizer.html', {'recipes': appetizer_recipes, 'user_profile': user_profile})


# Món Tráng Miện
@login_required
def dessert(request):
    dessert_class = Classify.objects.get(name='Món Á')
    dessert_recipes = Recipe.objects.filter(classify=dessert_class).select_related('author', 'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/dessert.html', {'recipes': dessert_recipes, 'user_profile': user_profile})


# Món Ăn Vặt
@login_required
def snacks(request):
    snacks_class = Classify.objects.get(name='Món Ăn Vặt')
    snacks_recipes = Recipe.objects.filter(classify=snacks_class).select_related('author', 'author__userprofile')
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'food/snacks.html', {'recipes': snacks_recipes, 'user_profile': user_profile})


# Post ----------------------------------------------------------------
@login_required
def postfood(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        classify_name = request.POST.get('classify')  # Lấy tên phân loại từ form
        introduce = request.POST.get('introduce')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')

        if not images:
            error = "Bạn cần tải lên ít nhất một hình ảnh."
            return render(request, 'appfood/postfood.html', {'error': error})

        if title and description and classify_name:
            # Tìm hoặc tạo phân loại
            classify, created = Classify.objects.get_or_create(name=classify_name)

            # Tạo công thức nấu ăn mới
            recipe = Recipe.objects.create(
                title=title,
                description=description,
                introduce=introduce,
                author=request.user
            )
            # Gán phân loại cho công thức
            recipe.classify.add(classify)
            # Lưu từng ảnh liên kết với công thức nấu ăn
            for image in images:
                RecipeImage.objects.create(recipe=recipe, image=image)

            # Tạo thông báo cho những người theo dõi
            followers = Follow.objects.filter(followed=request.user)
            for follow in followers:
                Notification.objects.create(
                    recipient=follow.follower,
                    sender=request.user,
                    recipess=recipe,
                    message=f'{request.user.last_name} {request.user.first_name} đã đăng một nội dung mới.',
                    read=False  # Trạng Thái Thông Báo Chưa xem
                )
                print(f'Thông báo tạo thành công cho {follow.follower.last_name} {follow.follower.first_name}')

            messages.success(request, 'Nội dung của bạn đã được đăng thành công.')
            return redirect('home')  # Chuyển hướng đến danh sách công thức
        else:
            error = "Bạn cần nhập đầy đủ tiêu đề, mô tả và chọn phân loại món ăn."
            return render(request, 'appfood/postfood.html', {'error': error})

    return render(request, 'appfood/postfood.html', {'user_profile': user_profile})


# User------------------------------------------------------------------------------------
@login_required
def list_user(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    users = User.objects.exclude(id=request.user.id).exclude(
        is_superuser=True)  # Loại Bỏ Admin và Bản Thân để dùng chức năng follow
    following = Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
    return render(request, 'user/list_user.html',
                  {'users': users, 'following': following, 'user_profile': user_profile})


@login_required
def notifications(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    notifications = request.user.notifications.all().order_by('-timestamp').select_related('sender__userprofile')
    # Đánh dấu tất cả các thông báo là đã đọc
    notifications.update(read=True)
    return render(request, 'appfood/notifications.html', {'notifications': notifications, 'user_profile': user_profile})


@login_required
def search_user(request):
    if request.method == 'POST':
        query = request.POST.get('searched')
        if query:
            users = User.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query),
                is_superuser=False
            )
        else:
            users = User.objects.none()
        following = Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        return render(request, 'user/search_user.html',
                      {'users': users, 'query': query, 'following': following, 'user_profile': user_profile})
    return render(request, 'user/search_user.html',
                  {'users': User.objects.none(), 'query': '', 'following': [], 'user_profile': user_profile})


@login_required
def page_user(request):
    # Số người theo dõi bạn
    followers_count = Follow.objects.filter(followed=request.user).count()
    # Số người bạn theo dõi
    following_count = Follow.objects.filter(follower=request.user).count()
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    recipes = Recipe.objects.filter(author=request.user).prefetch_related('images', 'classify')

    return render(request, 'user/page_user.html', {'user_profile': user_profile, 'followers_count': followers_count,
                                                   'following_count': following_count, 'recipes': recipes, })


@login_required
def edit_user(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        profile_image = request.FILES.get('profile_image')  # Đảm bảo lấy ảnh từ request.FILES

        user_profile.user.first_name = first_name
        user_profile.user.last_name = last_name

        if birth_date:
            user_profile.birth_date = birth_date
        else:
            user_profile.birth_date = None

        user_profile.gender = gender
        if profile_image:
            user_profile.profile_image = profile_image

        user_profile.user.save()
        user_profile.save()
        return redirect('page_user')

    return render(request, 'user/edit_user.html', {'user_profile': user_profile})


login_required


def detail_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    detail_user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    followers_count = Follow.objects.filter(followed=user).count()

    following_count = Follow.objects.filter(follower=user).count()
    # Danh sách công thức của người dùng này
    recipes = Recipe.objects.filter(author=user).prefetch_related('images', 'classify')

    return render(request, 'user/detail_user.html', {
        'user_profile': user_profile,
        'detail_user_profile': detail_user_profile,
        'followers_count': followers_count,
        'following_count': following_count,
        'recipes': recipes,
    })


# Follower - UnFollow
@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
    if created:
        # Tạo thông báo 
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            recipess=None,
            message=f'{request.user.last_name} {request.user.first_name} đã theo dõi bạn.',
            read=False
        )
        messages.success(request, f'Bạn đã theo dõi {user_to_follow.last_name} {user_to_follow.first_name} thành công.')
    else:
        messages.info(request, f'Bạn đã theo dõi {user_to_follow.last_name} {user_to_follow.first_name} trước đó rồi.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    follow = Follow.objects.filter(follower=request.user, followed=user_to_unfollow).first()
    if follow:
        follow.delete()
        messages.success(request, f'Bạn đã hủy theo dõi {user_to_unfollow.last_name} {user_to_unfollow.first_name}.')
    else:
        messages.info(request, f'Bạn chưa theo dõi {user_to_unfollow.last_name} {user_to_unfollow.first_name}.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

