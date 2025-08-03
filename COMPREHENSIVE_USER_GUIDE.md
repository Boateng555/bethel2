# Bethel Church Management Platform - Comprehensive User Guide

## Table of Contents
1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [User Roles and Permissions](#user-roles-and-permissions)
4. [Global Admin Guide](#global-admin-guide)
5. [Local Church Admin Guide](#local-church-admin-guide)
6. [Church Management](#church-management)
7. [Event Management](#event-management)
8. [Ministry Management](#ministry-management)
9. [News Management](#news-management)
10. [Sermon Management](#sermon-management)
11. [Donation System](#donation-system)
12. [Hero Banners and Media](#hero-banners-and-media)
13. [Content Pages](#content-pages)
14. [Global Features](#global-features)
15. [Troubleshooting](#troubleshooting)
16. [Best Practices](#best-practices)

---

## System Overview

The Bethel Church Management Platform is a comprehensive multi-tenant system designed to help Bethel churches worldwide manage their online presence, events, ministries, and communications. The platform supports both individual church websites and a global Bethel network site.

### Key Features
- **Multi-tenant Architecture**: Each church has its own isolated data and website
- **Smart Location Detection**: Automatically redirects visitors to their nearest church
- **Global Content Sharing**: Churches can request to feature content on the global site
- **Professional Templates**: Special templates for big events with registration systems
- **Media Management**: Advanced image and video handling with optimization
- **Donation Integration**: Multiple payment method support
- **Admin Dashboards**: Role-based admin interfaces

### System Architecture
- **Backend**: Django (Python)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Media Storage**: Local file system with optimization
- **Frontend**: Django templates with responsive design
- **Admin Interface**: Custom Django admin with role-based access

---

## Getting Started

### Accessing the System

1. **Global Admin Access**
   - URL: `https://your-domain.com/admin/`
   - Username: Provided by system administrator
   - Password: Provided by system administrator

2. **Local Church Admin Access**
   - URL: `https://your-domain.com/admin/`
   - Username: Created by global admin
   - Password: Set during account creation

### First-Time Setup

#### For Global Admins:
1. Log into the admin panel
2. Navigate to "Global Settings" and configure:
   - Site name and description
   - Global navigation logo
   - Contact information
   - Local church redirect settings
3. Set up the main global church fallback
4. Configure global features and permissions

#### For Local Church Admins:
1. Log into the admin panel
2. Update your church information in "Church Info"
3. Set up service times and contact details
4. Upload church logo and banner images
5. Configure donation methods
6. Create your first hero banner

---

## User Roles and Permissions

### Global Admin
**Full system access and control**
- Manage all churches and their admins
- Approve/reject global feature requests
- Configure global settings
- Manage global content (hero banners, events, news)
- Access all church data
- System configuration and maintenance

### Local Church Admin
**Church-specific management**
- Manage their church's information
- Create and manage events, ministries, news, sermons
- Upload and manage media content
- Handle donation methods
- Request global features for their content
- Manage church-specific pages (About, Leadership)

### Moderator
**Limited administrative access**
- View and moderate content
- Limited editing capabilities
- No global feature approval rights

---

## Global Admin Guide

### Managing Churches

#### Adding a New Church
1. Navigate to "Churches" in the admin panel
2. Click "Add Church"
3. Fill in required information:
   - **Church Information**: Name, description, pastor name
   - **Location**: Address, city, state/province, country, postal code
   - **Contact**: Phone, email, website
   - **Service Times**: Enter service schedule
   - **Media**: Upload logo, navigation logo, banner image
4. Set status flags (active, approved, featured)
5. Save the church

#### Setting Up Church Admin
1. Go to "Church Admins" in the admin panel
2. Click "Add Church Admin"
3. Select the user and church
4. Choose role (local_admin, global_admin, moderator)
5. Set as active
6. Save

#### Church Approval Process
1. Review church applications in "Church Applications"
2. Check all provided information
3. Approve or reject with notes
4. If approved, create church and admin accounts

### Global Content Management

#### Managing Global Hero Banners
1. Navigate to "Heroes" (global)
2. Create new hero banners for the global site
3. Add multiple images/videos for carousel
4. Set display order and active status
5. Configure buttons and links

#### Global Feature Requests
1. Review requests in "Global Feature Requests"
2. Check content quality and relevance
3. Approve or reject with notes
4. Set feature dates for approved content

### System Configuration

#### Global Settings
- **Site Information**: Name, description, contact details
- **Navigation**: Global logo and branding
- **Local Church Redirect**: Enable/disable automatic redirects
- **Distance Settings**: Configure maximum redirect distance

---

## Local Church Admin Guide

### Dashboard Overview

The local admin dashboard provides quick access to:
- Church information summary
- Recent events, ministries, news
- Pending global feature requests
- Quick statistics

### Church Information Management

#### Basic Information
1. Navigate to "Church Info" in your admin panel
2. Update church details:
   - **Name and Description**: Church name and mission
   - **Pastor Information**: Pastor's name and contact
   - **Location**: Complete address and coordinates
   - **Service Times**: Regular service schedule
   - **Contact**: Phone, email, website

#### Media Upload
- **Church Logo**: Main church logo (recommended: 400x400px)
- **Navigation Logo**: Small circular logo for nav bar (recommended: 300x300px)
- **Banner Image**: Hero banner image (recommended: 1200x600px)

#### Service Times Configuration
Enter service times in the format:
```
Sunday 9:00 AM & 11:00 AM
Wednesday 7:00 PM
Friday Prayer: 6:00 PM
```

---

## Church Management

### Church Profile Setup

#### Essential Information
- **Church Name**: Official church name
- **Slug**: URL-friendly name (auto-generated)
- **Description**: Church mission and vision
- **Pastor Name**: Current pastor or leader
- **Denomination**: Usually "Bethel"

#### Location Details
- **Address**: Full street address
- **City**: City name
- **State/Province**: State or province
- **Country**: Country name
- **Postal Code**: ZIP or postal code
- **Coordinates**: Latitude/longitude (auto-geocoded)

#### Contact Information
- **Phone**: Church phone number
- **Email**: Church email address
- **Website**: Church website URL
- **Shop URL**: Online store link (optional)

### Church Status Management

#### Status Flags
- **Active**: Church is operational
- **Approved**: Church has been reviewed and approved
- **Featured**: Church appears in featured listings

#### Service Times
Configure multiple service times:
- Sunday services (primary and secondary)
- Wednesday services
- Friday services
- Other special services

---

## Event Management

### Creating Events

#### Basic Event Information
1. Navigate to "Events" in your admin panel
2. Click "Add Event"
3. Fill in required fields:
   - **Title**: Event name
   - **Description**: Detailed event description
   - **Start/End Date**: Event timing
   - **Location**: Venue name
   - **Address**: Full address
   - **Event Type**: Service, prayer, youth, etc.

#### Event Types
- **Church Service**: Regular worship services
- **Prayer Meeting**: Prayer gatherings
- **Youth Event**: Youth-specific activities
- **Women's Fellowship**: Women's ministry events
- **Men's Fellowship**: Men's ministry events
- **Convention**: Large gatherings
- **Conference**: Educational events
- **Outreach**: Community service
- **Other**: Miscellaneous events

#### Registration Settings
- **Requires Registration**: Enable for events needing RSVP
- **Max Attendees**: Limit attendance numbers
- **Registration Deadline**: Last date to register
- **Registration Fee**: Cost to attend

#### Event Display Options
- **Featured**: Highlight on church website
- **Public**: Show to visitors
- **Big Event**: Use professional template
- **Show QR Code**: Display QR code for sharing

### Big Events (Professional Template)

For major events, enable "Big Event" to get:
- Professional landing page
- Registration form
- Countdown timer
- Detailed schedule
- Speaker profiles
- Media gallery

#### Setting Up Big Events
1. Create event with "Big Event" enabled
2. Add event speakers in the "Event Speakers" section
3. Create schedule items in "Schedule Items"
4. Upload event media (images/videos)
5. Configure registration settings

#### Event Speakers
- **Name**: Speaker's full name
- **Photo**: Professional headshot
- **Title**: Role or position
- **Bio**: Brief biography
- **Social Media**: Links to social profiles

#### Event Schedule
- **Day**: Which day of the event
- **Start/End Time**: Session timing
- **Title**: Session name
- **Description**: Session details
- **Speaker**: Who's leading
- **Location**: Where it's happening

### Global Event Features

#### Requesting Global Features
1. Enable "Request Global Feature" on your event
2. Fill in all required information
3. Submit for review
4. Global admins will review and approve/reject

#### Feature Status Tracking
- **None**: No request made
- **Pending**: Under review
- **Approved**: Will appear on global site
- **Rejected**: Not approved (with notes)

---

## Ministry Management

### Creating Ministries

#### Ministry Information
1. Navigate to "Ministries" in your admin panel
2. Click "Add Ministry"
3. Fill in details:
   - **Name**: Ministry name
   - **Description**: What the ministry does
   - **Ministry Type**: Category classification
   - **Leader**: Ministry leader's name
   - **Contact**: Email and phone for inquiries

#### Ministry Types
- **Youth Ministry**: Young people's activities
- **Women's Ministry**: Women's fellowship
- **Men's Ministry**: Men's fellowship
- **Children's Ministry**: Kids' programs
- **Music Ministry**: Worship and music
- **Prayer Ministry**: Prayer groups
- **Outreach Ministry**: Community service
- **Education Ministry**: Teaching and learning
- **Other**: Miscellaneous ministries

#### Ministry Settings
- **Active**: Currently operating
- **Featured**: Highlight on website
- **Public**: Show on global site

### Ministry Join Requests

#### Managing Requests
1. View join requests in the ministry admin
2. Review applicant information
3. Contact applicants as needed
4. Mark requests as reviewed

#### Request Information
- **Name**: Applicant's name
- **Email**: Contact email
- **Phone**: Contact phone
- **Message**: Why they want to join
- **Date**: When request was made

---

## News Management

### Creating News Articles

#### Article Content
1. Navigate to "News" in your admin panel
2. Click "Add News"
3. Fill in details:
   - **Title**: News headline
   - **Content**: Full article text
   - **Excerpt**: Brief summary (optional)
   - **Date**: Publication date
   - **Image**: Related photo

#### News Settings
- **Featured**: Highlight on website
- **Public**: Show to visitors
- **Global Feature**: Request global exposure

#### Content Guidelines
- Write clear, engaging headlines
- Include relevant images
- Keep content current and accurate
- Use proper formatting and structure

### Global News Features

#### Requesting Global Features
1. Enable "Request Global Feature" on news article
2. Ensure content is high quality
3. Submit for global admin review
4. Track approval status

---

## Sermon Management

### Uploading Sermons

#### Sermon Information
1. Navigate to "Sermons" in your admin panel
2. Click "Add Sermon"
3. Fill in details:
   - **Title**: Sermon title
   - **Preacher**: Who preached
   - **Description**: Sermon summary
   - **Date**: When preached
   - **Scripture**: Bible references
   - **Duration**: Length of sermon

#### Media Upload
- **Audio File**: MP3 format recommended
- **Video File**: MP4 format recommended
- **Thumbnail**: Preview image
- **External Link**: YouTube/Vimeo link

#### Sermon Settings
- **Featured**: Highlight on website
- **Public**: Show to visitors
- **Language**: Sermon language

### Sermon Organization

#### Scripture References
- Enter Bible passages (e.g., "John 3:16")
- Include full scripture text if desired
- Use standard Bible reference format

#### Media Management
- Upload high-quality audio/video
- Create engaging thumbnails
- Provide external links when available
- Ensure proper file formats

---

## Donation System

### Setting Up Donation Methods

#### Payment Types
1. Navigate to "Donation Methods" in your admin panel
2. Click "Add Donation Method"
3. Choose payment type:
   - **PayPal**: PayPal.me or PayPal Business
   - **Stripe**: Stripe payment links
   - **GoFundMe**: GoFundMe campaign links
   - **Bank Transfer**: Bank account details
   - **Check**: Mailing address for checks
   - **Cash**: In-person donations
   - **Other**: Custom payment methods

#### Configuration
- **Name**: Fund name (e.g., "General Fund", "Building Fund")
- **External Link**: Direct payment link
- **Account Info**: Payment details
- **Description**: What the fund supports
- **Active**: Enable/disable
- **Default**: Set as primary option

### Donation Page Setup

#### Page Configuration
- Display all active donation methods
- Show fund descriptions
- Provide clear payment instructions
- Include contact information

#### Best Practices
- Offer multiple payment options
- Provide clear fund descriptions
- Keep payment information secure
- Update regularly

---

## Hero Banners and Media

### Creating Hero Banners

#### Banner Configuration
1. Navigate to "Local Heroes" in your admin panel
2. Click "Add Local Hero"
3. Configure:
   - **Title**: Main headline
   - **Subtitle**: Supporting text
   - **Background**: Image or video
   - **Buttons**: Call-to-action buttons
   - **Order**: Display sequence

#### Media Management
- **Images**: Upload hero images (recommended: 1200x800px)
- **Videos**: Upload hero videos (MP4 format)
- **Order**: Set display sequence
- **Multiple Media**: Create carousel effects

#### Button Configuration
- **Primary Button**: Main call-to-action
- **Secondary Button**: Alternative action
- **Custom Links**: Direct to specific pages

### Global Hero Features

#### Requesting Global Features
1. Enable "Request Global Feature" on hero
2. Ensure high-quality content
3. Submit for review
4. Track approval status

#### Feature Requirements
- Professional quality images/videos
- Engaging content
- Proper sizing and formatting
- Relevant to global audience

---

## Content Pages

### About Page Management

#### Global About Page
1. Navigate to "About Page" in admin panel
2. Configure sections:
   - **Intro/Mission**: Church mission statement
   - **Founding Story**: Church history
   - **Timeline**: Key milestones
   - **Leadership Timeline**: Past leaders
   - **Ministry Today**: Current activities
   - **Quick Facts**: Important statistics

#### Local About Pages
Each church can have its own about page:
- Church-specific information
- Local history and mission
- Current leadership
- Local ministries and activities

### Leadership Page Management

#### Global Leadership
- **Introduction**: Leadership overview
- **Current Leadership**: Present leaders
- **Board Members**: Board information
- **Leadership Team**: Team details
- **Vision/Mission**: Statements

#### Local Leadership
- **Pastor Information**: Current pastor
- **Assistant Pastor**: Assistant pastor details
- **Board Members**: Local board
- **Leadership Team**: Local team
- **Photos**: Leadership photos

### Page Media

#### Image Uploads
- **Logos**: Church and organization logos
- **Leadership Photos**: Professional headshots
- **Group Photos**: Team and board photos
- **Additional Images**: Supporting visuals

#### Image Guidelines
- Use high-quality images
- Proper sizing and formatting
- Professional appearance
- Consistent style

---

## Global Features

### Content Sharing System

#### How It Works
1. Local admins create content (events, news, heroes)
2. Enable "Request Global Feature"
3. Global admins review content
4. Approved content appears on global site
5. Content is featured based on schedule

#### Feature Types
- **Hero Banners**: Featured on global homepage
- **Events**: Highlighted global events
- **News**: Global news articles

#### Approval Process
1. **Submission**: Local admin requests feature
2. **Review**: Global admin evaluates content
3. **Decision**: Approve or reject with notes
4. **Scheduling**: Set feature dates
5. **Publication**: Content goes live

### Global Admin Responsibilities

#### Content Review
- Evaluate content quality
- Check relevance to global audience
- Ensure proper formatting
- Verify accuracy

#### Feature Scheduling
- Set appropriate feature dates
- Avoid conflicts
- Maintain variety
- Consider seasonal relevance

#### Communication
- Provide feedback on rejections
- Explain approval decisions
- Guide content improvements
- Maintain relationships

---

## Troubleshooting

### Common Issues

#### Login Problems
- **Forgot Password**: Contact global admin
- **Account Locked**: Check with system admin
- **Wrong Permissions**: Verify role assignment

#### Content Not Appearing
- **Check Status**: Ensure content is active/public
- **Review Permissions**: Verify admin access
- **Clear Cache**: Refresh browser cache
- **Check Dates**: Verify publication dates

#### Media Upload Issues
- **File Size**: Check file size limits
- **Format**: Ensure proper file formats
- **Permissions**: Verify upload permissions
- **Storage**: Check available storage space

#### Global Feature Issues
- **Request Status**: Check approval status
- **Content Quality**: Review content standards
- **Timing**: Verify feature dates
- **Communication**: Contact global admin

### Getting Help

#### Support Channels
- **Global Admin**: Primary support contact
- **System Documentation**: This guide
- **Technical Support**: For system issues
- **Training**: Available for new users

#### Documentation Resources
- **User Guide**: This comprehensive guide
- **Admin Manual**: Technical documentation
- **Video Tutorials**: Step-by-step guides
- **FAQ**: Common questions and answers

---

## Best Practices

### Content Management

#### Writing Guidelines
- **Clear and Concise**: Write clearly and directly
- **Accurate Information**: Verify all details
- **Engaging Content**: Make content interesting
- **Regular Updates**: Keep content current

#### Media Guidelines
- **High Quality**: Use professional images/videos
- **Proper Sizing**: Follow recommended dimensions
- **Consistent Style**: Maintain brand consistency
- **Optimized Files**: Compress for web use

#### Organization
- **Consistent Naming**: Use clear, descriptive names
- **Proper Categorization**: Use appropriate tags/types
- **Regular Maintenance**: Update and clean content
- **Backup**: Keep copies of important content

### User Experience

#### Website Design
- **Mobile Friendly**: Ensure mobile compatibility
- **Fast Loading**: Optimize for speed
- **Easy Navigation**: Clear menu structure
- **Accessible**: Follow accessibility guidelines

#### Content Strategy
- **Regular Updates**: Post content regularly
- **Engaging Media**: Use images and videos
- **Clear Calls-to-Action**: Guide user actions
- **Relevant Information**: Provide useful content

### Administrative Efficiency

#### Workflow Management
- **Content Calendar**: Plan content in advance
- **Approval Process**: Streamline approvals
- **Quality Control**: Review before publishing
- **Performance Tracking**: Monitor effectiveness

#### Communication
- **Clear Instructions**: Provide clear guidance
- **Regular Updates**: Keep users informed
- **Feedback Loop**: Encourage user feedback
- **Training**: Provide ongoing training

### Security and Privacy

#### Data Protection
- **Secure Access**: Use strong passwords
- **Regular Backups**: Backup important data
- **Privacy Compliance**: Follow privacy laws
- **Access Control**: Limit access appropriately

#### System Maintenance
- **Regular Updates**: Keep system updated
- **Security Monitoring**: Monitor for issues
- **Performance Optimization**: Maintain speed
- **Disaster Recovery**: Plan for emergencies

---

## Conclusion

This comprehensive guide covers all aspects of the Bethel Church Management Platform. Whether you're a global admin managing the entire system or a local church admin managing your church's presence, this guide provides the information you need to effectively use the platform.

### Key Takeaways
- **Multi-tenant Architecture**: Each church has isolated data and functionality
- **Role-based Access**: Different permissions for different user types
- **Global Content Sharing**: Ability to feature local content globally
- **Professional Templates**: Special templates for major events
- **Comprehensive Management**: Complete control over church online presence

### Next Steps
1. **Complete Setup**: Finish initial configuration
2. **Content Creation**: Start adding church content
3. **Training**: Train additional users as needed
4. **Optimization**: Continuously improve content and processes
5. **Growth**: Expand features and capabilities

For additional support or questions, contact your global administrator or refer to the technical documentation provided with the system.

---

*This guide is maintained by the Bethel Church Management Platform team. For updates or corrections, please contact the system administrator.* 