# Church Setup Documentation

## Automatic Setup System

When a new church is created in the Bethel platform, it automatically gets set up with default functionality. This means you don't have to manually create ministries, donation methods, events, and other content every time.

### What Gets Created Automatically

When a new church is created, the following items are automatically set up:

#### 1. **Default Ministries** (7 ministries)
- Youth Ministry
- Women's Ministry  
- Men's Ministry
- Children's Ministry
- Music Ministry
- Prayer Ministry
- Outreach Ministry

Each ministry comes with:
- Pre-filled descriptions
- Default leader names
- Active status
- Public visibility

#### 2. **Default Donation Methods** (3 methods)
- General Fund (default)
- Building Fund
- Missions Fund

Each donation method includes:
- Contact information for church office
- Descriptions of fund purposes
- Active status

#### 3. **Default Hero Section**
- Welcome message with church name and location
- "Plan Your Visit" and "Watch Online" buttons
- Active status

#### 4. **Default Events** (2 events)
- **Sunday Service**: Weekly service at 10:00 AM
- **Prayer Meeting**: Weekly prayer meeting at 7:00 PM

Both events include:
- Church location and address
- Public visibility
- Proper date/time scheduling

#### 5. **Welcome News Article**
- Welcome message for the church
- Public visibility
- Current date

### How It Works

#### Automatic Setup (New Churches)
- When you create a new church in the admin, the setup happens automatically
- No manual intervention required
- All content is created with sensible defaults

#### Manual Setup (Existing Churches)
If you need to set up an existing church that doesn't have this content:

1. **Via Admin Action**:
   - Go to Churches list in admin
   - Select one or more churches
   - Choose "Set up default functionality" from the actions dropdown
   - Click "Go"

2. **Via Individual Church Page**:
   - Edit a specific church
   - Click the "Set Up Default Functionality" button
   - The setup will run immediately

3. **Via Management Command**:
   ```bash
   # Set up a specific church
   python manage.py setup_church_defaults --church-id <church-id>
   
   # Set up all churches
   python manage.py setup_church_defaults --all
   ```

### Customization

After the automatic setup, you can:
- Edit ministry details and add real leader names
- Update donation methods with actual payment links
- Customize the hero section with your own images and messages
- Modify event times and details
- Add more content as needed

### Benefits

- **Saves Time**: No need to manually create basic content
- **Consistency**: All churches start with the same structure
- **Completeness**: Ensures churches have all essential functionality
- **Flexibility**: Easy to customize after initial setup

### Technical Details

The automatic setup is handled by:
- **Signal**: `post_save` signal on the Church model
- **Method**: `setup_default_functionality()` method on Church model
- **Admin Action**: Bulk setup for multiple churches
- **Management Command**: Command-line setup option

All setup methods check if content already exists before creating new items, so it's safe to run multiple times.

## Support

If you need to modify the default content or add new default items, you can:

1. Edit the signal function in `core/models.py`
2. Update the management command in `core/management/commands/setup_church_defaults.py`
3. Run migrations if you add new model fields

This ensures that every new church on the Bethel platform starts with a complete, professional website that they can immediately customize for their specific needs. 