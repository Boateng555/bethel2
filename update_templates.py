#!/usr/bin/env python3
"""
Script to update all templates to use the new get_url methods instead of .url
"""
import os
import re

def update_template_file(file_path):
    """Update a single template file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Update HeroMedia
    content = re.sub(r'{{ media\.image\.url }}', '{{ media.get_image_url }}', content)
    content = re.sub(r'{{ media\.video\.url }}', '{{ media.get_video_url }}', content)
    
    # Update Church
    content = re.sub(r'{{ church\.logo\.url }}', '{{ church.get_logo_url }}', content)
    content = re.sub(r'{{ church\.banner_image\.url }}', '{{ church.get_banner_url }}', content)
    
    # Update Sermon
    content = re.sub(r'{{ sermon\.thumbnail\.url }}', '{{ sermon.get_thumbnail_url }}', content)
    content = re.sub(r'{{ sermon\.audio_file\.url }}', '{{ sermon.get_audio_url }}', content)
    content = re.sub(r'{{ sermon\.video_file\.url }}', '{{ sermon.get_video_url }}', content)
    
    # Update Ministry
    content = re.sub(r'{{ ministry\.image\.url }}', '{{ ministry.get_image_url }}', content)
    
    # Update News
    content = re.sub(r'{{ news\.image\.url }}', '{{ news.get_image_url }}', content)
    content = re.sub(r'{{ news_item\.image\.url }}', '{{ news_item.get_image_url }}', content)
    content = re.sub(r'{{ article\.image\.url }}', '{{ article.get_image_url }}', content)
    
    # Update EventHeroMedia
    content = re.sub(r'{{ media\.image\.url }}', '{{ media.get_image_url }}', content)
    content = re.sub(r'{{ media\.video\.url }}', '{{ media.get_video_url }}', content)
    
    # Update EventSpeaker
    content = re.sub(r'{{ speaker\.photo\.url }}', '{{ speaker.photo }}', content)
    
    # Update EventHighlight
    content = re.sub(r'{{ highlight\.image\.url }}', '{{ highlight.image }}', content)
    
    # Update AboutPage
    content = re.sub(r'{{ about_page\.logo\.url }}', '{{ about_page.logo }}', content)
    content = re.sub(r'{{ about_page\.founder_image\.url }}', '{{ about_page.founder_image }}', content)
    content = re.sub(r'{{ about_page\.extra_image\.url }}', '{{ about_page.extra_image }}', content)
    
    # Update LeadershipPage
    content = re.sub(r'{{ leadership_page\.chairman_image\.url }}', '{{ leadership_page.chairman_image }}', content)
    content = re.sub(r'{{ leadership_page\.vice_chairman_image\.url }}', '{{ leadership_page.vice_chairman_image }}', content)
    content = re.sub(r'{{ leadership_page\.board_image\.url }}', '{{ leadership_page.board_image }}', content)
    content = re.sub(r'{{ leadership_page\.team_image\.url }}', '{{ leadership_page.team_image }}', content)
    content = re.sub(r'{{ leadership_page\.leadership_photo_1\.url }}', '{{ leadership_page.leadership_photo_1 }}', content)
    content = re.sub(r'{{ leadership_page\.leadership_photo_2\.url }}', '{{ leadership_page.leadership_photo_2 }}', content)
    content = re.sub(r'{{ leadership_page\.leadership_photo_3\.url }}', '{{ leadership_page.leadership_photo_3 }}', content)
    
    # Update LocalLeadershipPage
    content = re.sub(r'{{ leadership_page\.pastor_image\.url }}', '{{ leadership_page.pastor_image }}', content)
    content = re.sub(r'{{ leadership_page\.assistant_pastor_image\.url }}', '{{ leadership_page.assistant_pastor_image }}', content)
    content = re.sub(r'{{ leadership_page\.board_image\.url }}', '{{ leadership_page.board_image }}', content)
    content = re.sub(r'{{ leadership_page\.team_image\.url }}', '{{ leadership_page.team_image }}', content)
    content = re.sub(r'{{ leadership_page\.leadership_photo_1\.url }}', '{{ leadership_page.leadership_photo_1 }}', content)
    content = re.sub(r'{{ leadership_page\.leadership_photo_2\.url }}', '{{ leadership_page.leadership_photo_2 }}', content)
    content = re.sub(r'{{ leadership_page\.leadership_photo_3\.url }}', '{{ leadership_page.leadership_photo_3 }}', content)
    
    # Update LocalAboutPage
    content = re.sub(r'{{ about_page\.about_photo_1\.url }}', '{{ about_page.about_photo_1 }}', content)
    content = re.sub(r'{{ about_page\.founder_image\.url }}', '{{ about_page.founder_image }}', content)
    content = re.sub(r'{{ about_page\.extra_image\.url }}', '{{ about_page.extra_image }}', content)
    
    # Update Hero background
    content = re.sub(r'{{ hero\.background_image\.url }}', '{{ hero.background_image }}', content)
    content = re.sub(r'{{ hero\.background_video\.url }}', '{{ hero.background_video }}', content)
    
    # Update Event card_image
    content = re.sub(r'{{ event\.card_image\.url }}', '{{ event.card_image }}', content)
    
    # Update Convention
    content = re.sub(r'{{ convention\.banner_image\.url }}', '{{ convention.banner_image }}', content)
    
    # Update EventHeroMedia for events
    content = re.sub(r'{{ first_media\.image\.url }}', '{{ first_media.get_image_url }}', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")
        return True
    else:
        print(f"⏭️  No changes: {file_path}")
        return False

def main():
    """Update all template files"""
    templates_dir = "templates"
    updated_count = 0
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if update_template_file(file_path):
                    updated_count += 1
    
    print(f"\n🎉 Updated {updated_count} template files!")

if __name__ == "__main__":
    main() 