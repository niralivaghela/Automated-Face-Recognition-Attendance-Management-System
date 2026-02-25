# Automated-Face-Recognition-Attendance-Management-System
# Face Detection Attendance System
## Complete Python Tkinter + MySQL + OpenCV Face Recognition

**✅ NO dlib / NO cmake required!** Uses OpenCV's built-in Haar Cascade for face detection.

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MySQL
Edit `database.py` line 13:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',  # <-- change this
    'database': 'face_attendance_db'
}
```

### 3. Run System Validation
```bash
python test_system.py
```

### 4. Start Application
```bash
python main.py
```

### 5. Login
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change password immediately after first login!**

---

## 📦 Requirements

### Software
- Python 3.8+
- MySQL Server 5.7+
- Webcam (built-in or USB)

### Python Packages
```bash
opencv-python>=4.8.0          # Face detection (NO dlib needed!)
mysql-connector-python>=8.0.0 # Database
Pillow>=10.0.0                # Image processing
pandas>=2.0.0                 # Reports
openpyxl>=3.1.0               # Excel export
numpy>=1.24.0                 # Numerical operations
twilio>=8.0.0                 # WhatsApp alerts (optional)
```

**Install all at once**:
```bash
pip install -r requirements.txt
```

---

## 🗄️ MySQL Setup

### Windows
1. Download MySQL Installer: https://dev.mysql.com/downloads/installer/
2. Install MySQL Server
3. Set root password during installation
4. Start MySQL service

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql_secure_installation
```

### macOS
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### Configure Database
1. Open `database.py`
2. Update `DB_CONFIG` with your MySQL password
3. Database and tables are created automatically on first run

---

## 📁 Project Structure

```
face_attendance/
├── main.py                  # Entry point
├── database.py              # MySQL + CSV database manager
├── login.py                 # Login window (password/OTP/Google)
├── dashboard.py             # Main dashboard with sidebar
├── attendance_module.py     # Live face recognition attendance
├── students_module.py       # Student CRUD + face capture
├── reports_module.py        # Reports with filters + export
├── settings_module.py       # Settings, password, admin mgmt
├── face_engine.py           # OpenCV face detection engine
├── auto_scheduler.py        # Background task scheduler
├── notification_service.py  # WhatsApp alerts via Twilio
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── SETUP_GUIDE.md          # Detailed setup instructions
├── test_system.py          # System validation script
├── student_photos/          # Captured student photos (auto-created)
└── attendance_csv/          # Daily CSV exports (auto-created)
```

---

## ✨ Features

### 🔐 Authentication
- **Password Login**: SHA-256 hashed passwords
- **Phone OTP Login**: SMS-based authentication
- **Google Sign-In**: OAuth integration (demo)
- **Multi-Admin Support**: Multiple admin accounts
- **Forgot Password**: Email-based password reset

### 👥 Student Management
- Add/Edit/Delete students
- Face capture with live camera preview
- Photo management
- Student profile with full history
- Active/Inactive status toggle
- Bulk import/export

### 📸 Attendance System
- **Live Face Recognition**: Real-time detection using OpenCV
- **Auto-Mark**: Automatic attendance on face match
- **Late Detection**: Auto-marks as "Late" after 9:00 AM
- **Manual Entry**: Mark attendance by Student ID
- **Today's Log**: Real-time attendance list
- **Duplicate Prevention**: One entry per student per day

### 📊 Reports & Analytics
- Filter by date, class, student
- Export to CSV/Excel
- Generate PDF reports
- Attendance statistics
- Student-wise attendance history
- Class-wise summaries
- Weekly/Monthly reports

### 👤 Student Profile System
- Complete attendance history
- Attendance percentage calculation
- Academic results & grades
- Photo management
- Individual reports export
- Shortage alerts (<75% attendance)

### 📱 Notifications (Optional)
- WhatsApp absent alerts to parents
- SMS notifications via Twilio
- Email summaries
- Configurable alert schedules

### ⏰ Auto-Scheduler
- **9:30 AM**: Send absent alerts
- **11:15 AM**: Auto-mark missing students as absent
- **6:00 PM**: Daily summary email
- **Friday 5 PM**: Weekly report
- **1st of month**: Monthly PDF report

### 📋 Activity Log
- Full audit trail of all actions
- User tracking
- Timestamp logging
- Export logs for compliance

### ⚙️ Settings
- Change password
- Update profile (name, email, phone)
- Add/manage admin accounts
- Database configuration
- System information

---

## 🎯 Usage Guide

### Adding Students

1. Click **Students** in sidebar
2. Click **➕ Add Student**
3. Fill in details:
   - Student ID (required)
   - Full Name (required)
   - Class, Section, Email, Phone (optional)
4. **Face Capture**:
   - Click **📷 Open Camera**
   - Position face in green box
   - Click **⚡ Capture Face**
   - Wait for "✅ Face captured successfully!"
5. Click **💾 Save Student**

### Taking Attendance

1. Click **Take Attendance** in sidebar
2. Click **▶ Start Camera**
3. Students stand in front of camera one by one
4. System automatically recognizes and marks attendance
   - **Green box** = Recognized ✅
   - **Red box** = Unknown ❌
5. Check **Recognized Today** panel on right
6. Click **⏹ Stop Camera** when done

### Manual Attendance

If camera fails or student face not recognized:

1. Click **✏️ Manual Mark** button
2. Enter Student ID
3. Select status (Present/Late/Absent)
4. Click **✅ Mark Attendance**

### Viewing Reports

1. Click **Reports** in sidebar
2. Apply filters:
   - **Date**: YYYY-MM-DD (e.g., 2024-03-15)
   - **Class**: Select from dropdown
   - **Student**: Enter ID or name
3. Click **🔍 Search**
4. Export:
   - **📥 CSV**: For Excel/Google Sheets
   - **📊 Excel**: Direct .xlsx file
   - **📄 PDF**: Professional report

### Student Profile

1. Click **👤 Student Profile** in sidebar
2. Search or select student from list
3. View:
   - Personal details
   - Attendance history
   - Attendance percentage
   - Academic results
4. Actions:
   - Edit details
   - Re-capture face
   - Add results
   - Export reports

---

## 🛠️ Troubleshooting

### Camera Not Opening

**Error**: "Cannot open camera!"

**Solutions**:
1. Close other apps using camera (Zoom, Teams, Skype)
2. Check camera permissions (Windows Settings → Privacy → Camera)
3. Try different camera index:
   - Open `attendance_module.py`
   - Line ~280: Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`
4. Restart computer

### Face Not Detected

**Issue**: Red box or no detection

**Solutions**:
1. Ensure good lighting
2. Look directly at camera
3. Remove glasses/mask if possible
4. Move closer (60cm - 1m distance)
5. Adjust sensitivity in `face_engine.py`:
   ```python
   minSize=(40, 40)  # Lower = more sensitive
   ```

### MySQL Connection Error

**Error**: "Access denied for user 'root'@'localhost'"

**Solutions**:
1. Verify password in `database.py`
2. Check MySQL service is running:
   ```bash
   # Windows: services.msc → MySQL → Start
   # Linux: sudo systemctl status mysql
   ```
3. Reset MySQL password if needed

### Import Errors

**Error**: "ModuleNotFoundError: No module named 'cv2'"

**Solution**:
```bash
pip install opencv-python --upgrade
```

### Slow Performance

**Issue**: Camera lag or freezing

**Solutions**:
1. Close other heavy applications
2. Lower camera resolution in `attendance_module.py`:
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH,  480)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
   ```
3. Increase frame skip:
   ```python
   PROCESS_EVERY = 5  # Process every 5th frame
   ```

**For detailed troubleshooting, see `SETUP_GUIDE.md`**

---

## 📱 WhatsApp Alerts Setup (Optional)

### Prerequisites
- Twilio account (free trial: $15 credit)
- WhatsApp Business API sandbox

### Quick Setup

1. **Create Twilio Account**: https://www.twilio.com/try-twilio
2. **Get Credentials**: Dashboard → Account Info
3. **Configure Sandbox**: Console → Messaging → Try WhatsApp
4. **Update `notification_service.py`**:
   ```python
   ACCOUNT_SID = 'your_account_sid'
   AUTH_TOKEN  = 'your_auth_token'
   ENABLED     = True
   ```
5. **Parent Setup** (one-time):
   - Parent sends WhatsApp to **+1 415 523 8886**
   - Message: `join your-sandbox-code`

**Detailed guide in `SETUP_GUIDE.md`**

---

## 🔐 Security

### Password Security
- SHA-256 hashing
- Minimum 6 characters
- Change default password immediately
- Password reset via email

### Database Security
- Parameterized queries (SQL injection prevention)
- Separate user accounts recommended
- Regular backups

### Activity Logging
- All actions logged with timestamp
- User tracking
- Audit trail for compliance

### Best Practices
1. Change default admin password
2. Use strong passwords
3. Regular database backups
4. Restrict database access
5. Keep system updated

---

## 🎓 System Validation

Run validation script to check all components:

```bash
python test_system.py
```

This checks:
- ✅ Python version
- ✅ Required modules
- ✅ Camera access
- ✅ Face detection engine
- ✅ Database connection
- ✅ File structure

---

## 📚 Documentation

- **README.md** (this file): Quick start guide
- **SETUP_GUIDE.md**: Detailed setup instructions
- **test_system.py**: System validation script
- **requirements.txt**: Python dependencies

---

## 🔄 Updates & Maintenance

### Daily
- Check attendance marked correctly
- Verify camera working
- Review activity log

### Weekly
- Backup database
- Export attendance reports
- Check disk space

### Monthly
- Update student records
- Archive old data
- Review system performance
- Update passwords

---

## 🎉 Success Checklist

- [ ] Python 3.8+ installed
- [ ] MySQL Server running
- [ ] Dependencies installed
- [ ] Database configured
- [ ] System validation passed
- [ ] Logged in successfully
- [ ] Default password changed
- [ ] First student added
- [ ] Face capture working
- [ ] Attendance taken
- [ ] Reports generated

---

## 💡 Tips & Tricks

### Better Face Recognition
- Good lighting is crucial
- Face camera directly
- Consistent distance (60cm - 1m)
- Capture multiple angles if needed
- Re-capture if recognition fails

### Performance Optimization
- Close unnecessary applications
- Use lower camera resolution
- Process fewer frames
- Regular database cleanup

### Data Management
- Export reports regularly
- Backup database weekly
- Archive old attendance data
- Clean up old photos

---

## 🏆 Features Comparison

| Feature | This System | Traditional |
|---------|-------------|-------------|
| Face Recognition | ✅ OpenCV (no dlib) | ❌ Requires dlib/cmake |
| Setup Time | 5 minutes | 2+ hours |
| Dependencies | 7 packages | 15+ packages |
| Camera Support | Any webcam | Specific models |
| Offline Mode | ✅ Yes | ❌ Cloud required |
| Cost | Free | Subscription |
| Customizable | ✅ Full source | ❌ Closed source |

---

## 📞 Support

### Common Issues

**Q: Camera not working?**  
A: Close other apps, check permissions, try index 1

**Q: Face not detected?**  
A: Better lighting, look at camera, remove glasses

**Q: MySQL error?**  
A: Check service running, verify password

**Q: Slow performance?**  
A: Lower resolution, close other apps

**Q: Can I use without webcam?**  
A: Yes, use Manual Attendance feature

### Getting Help

1. Check `SETUP_GUIDE.md` for detailed instructions
2. Run `python test_system.py` to diagnose issues
3. Review error messages in console
4. Check `scheduler.log` for background task errors

---

## 🚀 Advanced Features

### Auto-Scheduler
Background tasks run automatically:
- Absent alerts at 9:30 AM
- Auto-mark absent at 11:15 AM
- Daily summaries at 6:00 PM
- Weekly reports on Fridays
- Monthly reports on 1st

### Student Profile System
Complete student management:
- Full attendance history
- Academic results tracking
- Percentage calculations
- Individual reports
- Photo management

### Multiple Login Methods
- Username/Password
- Email/Password
- Phone OTP
- Google Sign-In

---

## 📝 License

Educational Use

---

## 🙏 Credits

Built with:
- **Python**: Programming language
- **OpenCV**: Face detection (NO dlib required!)
- **MySQL**: Database
- **Tkinter**: GUI framework
- **Pandas**: Data processing
- **Twilio**: WhatsApp notifications

---

## 🎯 Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Validate system
python test_system.py

# Run application
python main.py

# Backup database
mysqldump -u root -p face_attendance_db > backup.sql

# Restore database
mysql -u root -p face_attendance_db < backup.sql
```

---

**Version**: 1.0  
**Built for**: Vanita Vishram Women's University  
**Technology**: Python + OpenCV + MySQL + Tkinter  
**No dlib/cmake required!** ✅
