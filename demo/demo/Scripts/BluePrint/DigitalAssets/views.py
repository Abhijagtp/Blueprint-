from django.shortcuts import render

# Create your views here.


def digitalassets_view(request):
    return render(request, 'digitalassets.html')


def ibw_view(request):
    return render(request, 'IBW.html')


from django.shortcuts import redirect
from django.shortcuts import render
from .models import Blog, UserProfile

def blogs_views(request):
    # Pass the blogs to the template
    return render(request, 'blogs.html')


def Whitepaper_view(request):
    return render(request, 'whitepapers.html')


import json
import base64
import uuid
import os
import re
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Insight, UserProfile, Post
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)

@login_required
@csrf_exempt
def save_insight(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        logger.info(f"Received data: {data}")

        user_profile = UserProfile.objects.get(user=request.user)

        title = data.get('title', '').strip()
        summary = data.get('summary', '').strip()
        sources = data.get('sources', [])
        language = data.get('language', 'en').strip()
        categories = data.get('categories', [])
        content = data.get('content', '')
        is_draft = data.get('is_draft', False)  # Default to False (posted) unless specified
        insight_id = data.get('id')  # Get ID if present for updates

        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)

        # Process base64 images in content
        if '<img' in content:
            def replace_base64_images(match):
                img_tag = match.group(0)
                src_match = re.search(r'src="data:image/([^;]+);base64,([^"]+)"', img_tag)
                if src_match:
                    img_format, base64_data = src_match.groups()
                    try:
                        ext = img_format.split('/')[-1]
                        file_name = f"image_{uuid.uuid4()}.{ext}"
                        decoded_data = base64.b64decode(base64_data)
                        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'wb') as f:
                            f.write(decoded_data)
                        img_url = f"{settings.MEDIA_URL}{file_name}"
                        return img_tag.replace(f'src="data:image/{img_format};base64,{base64_data}"', f'src="{img_url}"')
                    except Exception as e:
                        logger.error(f"Error decoding base64 image: {str(e)}")
                        return img_tag
                return img_tag
            content = re.sub(r'<img[^>]+>', replace_base64_images, content)

        # Update or create insight
        if insight_id:
            try:
                insight = Insight.objects.get(id=insight_id, user_profile=user_profile)
                was_draft = insight.is_draft  # Store the previous is_draft value
                logger.info(f"Updating insight {insight_id}: was_draft={was_draft}, is_draft={is_draft}")

                insight.title = title
                insight.summary = summary
                insight.sources = sources
                insight.language = language
                insight.categories = categories
                insight.content = content
                insight.is_draft = is_draft
                insight.save()

                # Check if a Post already exists to avoid duplicates
                post_exists = Post.objects.filter(
                    content_type='insight',
                    content_id=insight.id,
                    user_profile=user_profile
                ).exists()
                logger.info(f"Post exists for insight {insight.id}: {post_exists}")

                # Create a Post entry if the insight is posted and no Post exists
                if not is_draft and not post_exists:
                    logger.info(f"Creating Post for insight {insight.id} (is_draft={is_draft}, was_draft={was_draft})")
                    post = Post.objects.create(
                        user_profile=user_profile,
                        content_type='insight',
                        content_id=insight.id,
                        caption=None,  # No caption needed for insight posts
                        image=None     # No image needed for insight posts
                    )
                    # Share to social media
                    share_success = share_to_social_media(post)
                    if not share_success:
                        logger.warning(f"Social media sharing failed for post {post.id}")

                message = 'Insight updated successfully'
            except Insight.DoesNotExist:
                logger.error(f"Insight {insight_id} not found for user {request.user.username}")
                return JsonResponse({'success': False, 'error': 'Insight not found'}, status=404)
        else:
            logger.info(f"Creating new insight: is_draft={is_draft}")
            insight = Insight(
                user_profile=user_profile,
                title=title,
                summary=summary,
                sources=sources,
                language=language,
                categories=categories,
                content=content,
                is_draft=is_draft
            )
            insight.save()

            # If the insight is created as a posted insight (not a draft), create a Post entry
            if not is_draft:
                logger.info(f"Creating Post for new insight {insight.id} (direct post)")
                post = Post.objects.create(
                    user_profile=user_profile,
                    content_type='insight',
                    content_id=insight.id,
                    caption=None,
                    image=None
                )
              
            message = 'Insight posted successfully' if not is_draft else 'Insight saved as draft'

        return JsonResponse({'success': True, 'message': message, 'id': insight.id}, status=201)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except UserProfile.DoesNotExist:
        logger.error(f"User profile not found for user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'User profile not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in save_insight: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Blog, Whitepaper, Insight
from Users.models import Post
import json

@login_required
def get_assets(request):
    user_profile = request.user.userprofile
    
    # Fetch all Blogs
    blogs = Blog.objects.filter(user_profile=user_profile).order_by('-created_at')
    blog_list = [
        {
            'id': blog.id,
            'type': 'blog',
            'title': blog.title,
            'summary': blog.content[:200] + '...' if len(blog.content) > 200 else blog.content,
            'last_updated': blog.created_at.isoformat(),
            'is_draft': blog.is_draft
        } for blog in blogs
    ]
    
    # Fetch all Whitepapers
    whitepapers = Whitepaper.objects.filter(user_profile=user_profile).order_by('-created_at')
    whitepaper_list = [
        {
            'id': whitepaper.id,
            'type': 'whitepaper',
            'title': whitepaper.title,
            'summary': whitepaper.summary[:200] + '...' if len(whitepaper.summary) > 200 else whitepaper.summary,
            'last_updated': whitepaper.created_at.isoformat(),
            'is_draft': whitepaper.is_draft
        } for whitepaper in whitepapers
    ]
    
    # Fetch all Insights
    insights = Insight.objects.filter(user_profile=user_profile).order_by('-created_at')
    insight_list = [
        {
            'id': insight.id,
            'type': 'insight',
            'title': insight.title,
            'summary': insight.summary or (insight.content[:200] + '...' if len(insight.content) > 200 else insight.content),
            'last_updated': insight.created_at.isoformat(),
            'is_draft': insight.is_draft
        } for insight in insights
    ]
    
    # Combine all assets into a single list
    all_assets = blog_list + whitepaper_list + insight_list
    all_assets.sort(key=lambda x: x['last_updated'], reverse=True)
    
    return JsonResponse({'success': True, 'assets': all_assets})





# For Blogs
@login_required
def get_blog(request, blog_id):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        blog = Blog.objects.get(id=blog_id, user_profile=user_profile)
        
        blog_data = {
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'language': blog.language,
            'categories': blog.categories,
            'thumbnail': blog.thumbnail.url if blog.thumbnail else '',
            'media_files': blog.media_files,
            'is_draft': blog.is_draft,
        }
        return JsonResponse({'success': True, 'blog': blog_data})
    except Blog.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Blog not found'}, status=404)
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User profile not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def delete_blog(request, blog_id):
    if request.method == 'POST':
        try:
            blog = Blog.objects.get(id=blog_id, user_profile=request.user.userprofile)
            blog.delete()
            return JsonResponse({'success': True})
        except Blog.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Blog not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# For Whitepapers
@login_required
def get_whitepaper(request, whitepaper_id):
    try:
        whitepaper = Whitepaper.objects.get(id=whitepaper_id, user_profile=request.user.userprofile)
        whitepaper_data = {
            'id': whitepaper.id,
            'title': whitepaper.title,
            'summary': whitepaper.summary,
            'sources': whitepaper.sources,
            'categories': whitepaper.categories,
            'content': whitepaper.content,
            'is_draft': whitepaper.is_draft
        }
        return JsonResponse({'success': True, 'whitepaper': whitepaper_data})
    except Whitepaper.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Whitepaper not found'})

@login_required
def delete_whitepaper(request, whitepaper_id):
    if request.method == 'POST':
        try:
            whitepaper = Whitepaper.objects.get(id=whitepaper_id, user_profile=request.user.userprofile)
            whitepaper.delete()
            return JsonResponse({'success': True})
        except Whitepaper.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Whitepaper not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_insight(request, insight_id):
    try:
        insight = Insight.objects.get(id=insight_id, user_profile=request.user.userprofile)
        insight_data = {
            'id': insight.id,
            'title': insight.title,
            'content': insight.content,
            'summary': insight.summary,
            'is_draft': insight.is_draft
        }
        return JsonResponse({'success': True, 'insight': insight_data})
    except Insight.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Insight not found'})

@login_required
def delete_insight(request, insight_id):
    if request.method == 'POST':
        try:
            insight = Insight.objects.get(id=insight_id, user_profile=request.user.userprofile)
            insight.delete()
            return JsonResponse({'success': True})
        except Insight.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Insight not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# For Blogs



import json
import base64
import uuid
import os
import re
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Blog, UserProfile, Post
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)



@login_required
@csrf_exempt
def save_blog(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_profile = UserProfile.objects.get(user=request.user)

        title = data.get('title', '').strip()
        content = data.get('content', '')
        language = data.get('language', 'en').strip()
        categories = data.get('categories', [])
        thumbnail_base64 = data.get('thumbnail', '')
        media_files_base64 = data.get('media_files', [])
        is_draft = data.get('is_draft', False)
        blog_id = data.get('id')

        # Log the incoming data for debugging
        logger.info(f"Received data: {data}")

        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)

        thumbnail_file = None
        if thumbnail_base64 and thumbnail_base64.startswith('data:image'):
            format_match = re.match(r'data:image/([^;]+);base64,(.+)', thumbnail_base64)
            if format_match:
                img_format, base64_data = format_match.groups()
                ext = img_format.split('/')[-1]
                file_name = f"thumbnail_{uuid.uuid4()}.{ext}"
                decoded_data = base64.b64decode(base64_data)
                thumbnail_file = ContentFile(decoded_data, name=file_name)

        media_urls = []
        for media_base64 in media_files_base64:
            if media_base64.startswith('data:image'):
                format_match = re.match(r'data:image/([^;]+);base64,(.+)', media_base64)
                if format_match:
                    img_format, base64_data = format_match.groups()
                    ext = img_format.split('/')[-1]
                    file_name = f"media_{uuid.uuid4()}.{ext}"
                    decoded_data = base64.b64decode(base64_data)
                    file_path = os.path.join(settings.MEDIA_ROOT, 'blog_media', file_name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(decoded_data)
                    media_urls.append(f"{settings.MEDIA_URL}blog_media/{file_name}")
            else:
                media_urls.append(media_base64)  # Preserve existing URLs

        if '<img' in content:
            def replace_base64_images(match):
                img_tag = match.group(0)
                src_match = re.search(r'src="data:image/([^;]+);base64,([^"]+)"', img_tag)
                if src_match:
                    img_format, base64_data = src_match.groups()
                    ext = img_format.split('/')[-1]
                    file_name = f"inline_{uuid.uuid4()}.{ext}"
                    decoded_data = base64.b64decode(base64_data)
                    file_path = os.path.join(settings.MEDIA_ROOT, 'blog_media', file_name)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'wb') as f:
                        f.write(decoded_data)
                    img_url = f"{settings.MEDIA_URL}blog_media/{file_name}"
                    return img_tag.replace(f'src="data:image/{img_format};base64,{base64_data}"', f'src="{img_url}"')
                return img_tag
            content = re.sub(r'<img[^>]+>', replace_base64_images, content)

        if blog_id:
            try:
                blog = Blog.objects.get(id=blog_id, user_profile=user_profile)
                was_draft = blog.is_draft  # Store the previous is_draft value
                logger.info(f"Updating blog {blog_id}: was_draft={was_draft}, is_draft={is_draft}")

                blog.title = title
                blog.content = content
                blog.language = language
                blog.categories = categories
                if thumbnail_file:
                    blog.thumbnail = thumbnail_file
                blog.media_files = media_urls
                blog.is_draft = is_draft
                blog.save()

                # Check if a Post already exists to avoid duplicates
                post_exists = Post.objects.filter(
                    content_type='blog',
                    content_id=blog.id,
                    user_profile=user_profile
                ).exists()
                logger.info(f"Post exists for blog {blog.id}: {post_exists}")

                # Create a Post entry if the blog is posted and no Post exists
                if not is_draft and not post_exists:
                    logger.info(f"Creating Post for blog {blog.id} (is_draft={is_draft}, was_draft={was_draft})")
                    post = Post.objects.create(
                        user_profile=user_profile,
                        content_type='blog',
                        content_id=blog.id,
                        caption=None,  # No caption needed for blog posts
                        image=None     # No image needed for blog posts
                    )
                

                message = 'Blog updated successfully'
            except Blog.DoesNotExist:
                logger.error(f"Blog {blog_id} not found for user {request.user.username}")
                return JsonResponse({'success': False, 'error': 'Blog not found'}, status=404)
        else:
            logger.info(f"Creating new blog: is_draft={is_draft}")
            blog = Blog(
                user_profile=user_profile,
                title=title,
                content=content,
                language=language,
                categories=categories,
                thumbnail=thumbnail_file,
                media_files=media_urls,
                is_draft=is_draft
            )
            blog.save()

            # If the blog is created as a posted blog (not a draft), create a Post entry
            if not is_draft:
                logger.info(f"Creating Post for new blog {blog.id} (direct post)")
                post = Post.objects.create(
                    user_profile=user_profile,
                    content_type='blog',
                    content_id=blog.id,
                    caption=None,  # No caption needed for blog posts
                    image=None     # No image needed for blog posts
                )
                

            message = 'Blog saved successfully'

        return JsonResponse({'success': True, 'message': message, 'id': blog.id}, status=201)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except UserProfile.DoesNotExist:
        logger.error(f"User profile not found for user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'User profile not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in save_blog: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    


# For Whitepapers


import json
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Whitepaper, UserProfile, Post
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

# Function to share the post to social media (placeholder)
def share_to_social_media(post):
    """
    Share the post to social media platforms.
    This is a placeholder function - replace with actual social media API calls.
    """
    try:
        content_url = f"https://yourdomain.com/{post.content_type}/{post.content_id}"
        message = f"New {post.content_type} posted - Check it out at {content_url} #{post.content_type.capitalize()} #NewPost"
        logger.info(f"Shared post {post.id} ({post.content_type} {post.content_id}) to social media: {message}")
        # Add your actual social media sharing logic here
        return True
    except Exception as e:
        logger.error(f"Error sharing post {post.id} to social media: {str(e)}")
        return False

@login_required
@csrf_exempt
def save_whitepaper(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_profile = UserProfile.objects.get(user=request.user)

        title = data.get('title', '').strip()
        summary = data.get('summary', '')
        content = data.get('content', '')
        sources = data.get('sources', [])
        categories = data.get('categories', [])
        is_draft = data.get('is_draft', False)  # Default to False (posted) unless specified
        whitepaper_id = data.get('id')

        # Log the incoming data for debugging
        logger.info(f"Received data: {data}")

        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)

        if whitepaper_id:
            try:
                whitepaper = Whitepaper.objects.get(id=whitepaper_id, user_profile=user_profile)
                was_draft = whitepaper.is_draft  # Store the previous is_draft value
                logger.info(f"Updating whitepaper {whitepaper_id}: was_draft={was_draft}, is_draft={is_draft}")

                whitepaper.title = title
                whitepaper.summary = summary
                whitepaper.content = content
                whitepaper.sources = sources
                whitepaper.categories = categories
                whitepaper.is_draft = is_draft
                whitepaper.save()

                # Check if a Post already exists to avoid duplicates
                post_exists = Post.objects.filter(
                    content_type='whitepaper',
                    content_id=whitepaper.id,
                    user_profile=user_profile
                ).exists()
                logger.info(f"Post exists for whitepaper {whitepaper.id}: {post_exists}")

                # Create a Post entry if the whitepaper is posted and no Post exists
                if not is_draft and not post_exists:
                    logger.info(f"Creating Post for whitepaper {whitepaper.id} (is_draft={is_draft}, was_draft={was_draft})")
                    post = Post.objects.create(
                        user_profile=user_profile,
                        content_type='whitepaper',
                        content_id=whitepaper.id,
                        caption=None,  # No caption needed for whitepaper posts
                        image=None     # No image needed for whitepaper posts
                    )
                    # Share to social media
                    share_success = share_to_social_media(post)
                    if not share_success:
                        logger.warning(f"Social media sharing failed for post {post.id}")

                message = 'Whitepaper updated successfully'
            except Whitepaper.DoesNotExist:
                logger.error(f"Whitepaper {whitepaper_id} not found for user {request.user.username}")
                return JsonResponse({'success': False, 'error': 'Whitepaper not found'}, status=404)
        else:
            logger.info(f"Creating new whitepaper: is_draft={is_draft}")
            whitepaper = Whitepaper(
                user_profile=user_profile,
                title=title,
                summary=summary,
                content=content,
                sources=sources,
                categories=categories,
                is_draft=is_draft
            )
            whitepaper.save()

            # If the whitepaper is created as a posted whitepaper (not a draft), create a Post entry
            if not is_draft:
                logger.info(f"Creating Post for new whitepaper {whitepaper.id} (direct post)")
                post = Post.objects.create(
                    user_profile=user_profile,
                    content_type='whitepaper',
                    content_id=whitepaper.id,
                    caption=None,
                    image=None
                )
                # Share to social media
                share_success = share_to_social_media(post)
                if not share_success:
                    logger.warning(f"Social media sharing failed for post {post.id}")

            message = 'Whitepaper saved successfully'

        return JsonResponse({'success': True, 'message': message, 'id': whitepaper.id}, status=201)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except UserProfile.DoesNotExist:
        logger.error(f"User profile not found for user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'User profile not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in save_whitepaper: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@csrf_exempt
def save_whitepaper_draft(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        user_profile = UserProfile.objects.get(user=request.user)

        logger.info(f"Creating new whitepaper draft: {data}")

        whitepaper = Whitepaper(
            user_profile=user_profile,
            title=data.get('title', 'Untitled Draft'),
            summary=data.get('summary', ''),
            content=data.get('content', ''),
            sources=data.get('sources', []),
            categories=data.get('categories', []),
            is_draft=True
        )
        whitepaper.save()
        return JsonResponse({'success': True, 'message': 'Whitepaper draft saved successfully', 'id': whitepaper.id}, status=201)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received in save_whitepaper_draft")
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except UserProfile.DoesNotExist:
        logger.error(f"User profile not found for user {request.user.username}")
        return JsonResponse({'success': False, 'error': 'User profile not found'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in save_whitepaper_draft: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# View Asset 


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Blog, Whitepaper, Insight  # Adjust based on your models
from django.contrib.auth.decorators import login_required

@login_required
def view_asset(request, asset_type, asset_id):
    type_map = {
        'blog': Blog,
        'whitepaper': Whitepaper,
        'insight': Insight
    }
    model = type_map.get(asset_type)
    if not model:
        return render(request, '404.html', status=404)

    asset = get_object_or_404(model, id=asset_id, user_profile=request.user.userprofile)

    # Handle media_files conditionally based on asset type
    media_files_list = []
    if asset_type == 'blog':
        media_files_list = asset.media_files  # media_files is a JSONField in Blog
    elif asset_type == 'whitepaper':
        # Whitepaper does not have media_files, so use an empty list
        media_files_list = []
    elif asset_type == 'insight':
        # Insight does not have media_files, so use an empty list
        media_files_list = []

    context = {
        'asset': asset,
        'asset_type': asset_type,
        'media_files': media_files_list  # Pass the list (empty or populated)
    }
    return render(request, 'view_asset.html', context)

@login_required
def edit_asset(request, asset_type, asset_id):
    type_map = {
        'blog': ('Blogs', Blog),
        'whitepaper': ('Whitepapers', Whitepaper),
        'insight': ('ibw', Insight)
    }
    redirect_name, model = type_map.get(asset_type, (None, None))
    if not model:
        return render(request, '404.html', status=404)

    asset = get_object_or_404(model, id=asset_id, user_profile=request.user.userprofile)
    data = {
        'id': asset.id,
        'title': asset.title,
        'content': asset.content,
        'language': asset.language,
        'categories': asset.categories,
        'thumbnail': asset.thumbnail.url if asset.thumbnail else '',
        'media_files': asset.media_files,
        'is_draft': asset.is_draft
    }
    request.session['currentAsset'] = data
    return HttpResponseRedirect(reverse(redirect_name))




# Details Page 
from django.shortcuts import render, get_object_or_404
from .models import Blog, Whitepaper, Insight, Post

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    # Fetch the associated Post object
    post = get_object_or_404(Post, content_type="blog", content_id=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog, 'post': post})

def whitepaper_detail(request, whitepaper_id):
    whitepaper = get_object_or_404(Whitepaper, id=whitepaper_id)
    # Fetch the associated Post object
    post = get_object_or_404(Post, content_type="whitepaper", content_id=whitepaper_id)
    return render(request, 'whitepaper_detail.html', {'whitepaper': whitepaper, 'post': post})

def insight_detail(request, insight_id):
    insight = get_object_or_404(Insight, id=insight_id)
    # Fetch the associated Post object
    post = get_object_or_404(Post, content_type="insight", content_id=insight_id)
    return render(request, 'insight_detail.html', {'insight': insight, 'post': post})


# view all @login_required
def view_all_assets_view(request):
    return render(request, 'view_all_assets.html')
