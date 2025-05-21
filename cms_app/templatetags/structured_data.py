import json
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.sites.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def page_structured_data(context, page):
    """Generate JSON-LD structured data for a page"""
    request = context['request']
    site = Site.objects.get_current()
    domain = f"https://{site.domain}" if request.is_secure() else f"http://{site.domain}"
    url = domain + reverse('cms_app:page_detail', kwargs={'slug': page.slug})
    
    data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": page.title,
        "description": page.meta_description or "",
        "url": url,
        "dateModified": page.updated_at.isoformat(),
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data)}</script>')


@register.simple_tag(takes_context=True)
def blog_post_structured_data(context, post):
    """Generate JSON-LD structured data for a blog post"""
    request = context['request']
    site = Site.objects.get_current()
    domain = f"https://{site.domain}" if request.is_secure() else f"http://{site.domain}"
    url = domain + reverse('cms_app:blog_detail', kwargs={'slug': post.slug})
    
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.meta_description or post.excerpt or "",
        "url": url,
        "datePublished": post.published_at.isoformat() if post.published_at else post.created_at.isoformat(),
        "dateModified": post.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "name": post.author.get_full_name() or post.author.email,
        },
        "publisher": {
            "@type": "Organization",
            "name": site.name,
            "logo": {
                "@type": "ImageObject",
                "url": f"{domain}/static/img/logo.png"
            }
        }
    }
    
    # Add image if available
    if post.featured_image:
        data["image"] = domain + post.featured_image.url
    
    # Add categories
    if post.categories.exists():
        data["keywords"] = ", ".join([category.name for category in post.categories.all()])
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data)}</script>')


@register.simple_tag(takes_context=True)
def organization_structured_data(context):
    """Generate JSON-LD structured data for the organization"""
    request = context['request']
    site = Site.objects.get_current()
    domain = f"https://{site.domain}" if request.is_secure() else f"http://{site.domain}"
    
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site.name,
        "url": domain,
        "logo": f"{domain}/static/img/logo.png",
        "sameAs": [
            "https://facebook.com/cozywish",
            "https://twitter.com/cozywish",
            "https://instagram.com/cozywish",
            "https://linkedin.com/company/cozywish"
        ]
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data)}</script>')
