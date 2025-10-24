# 🔐 Shift Handover App - Complete Login Credentials

## 📊 System Overview
- **Total Accounts:** 2
- **Total Teams:** 4 (2 per account)
- **Total Users:** 17
- **Application URL:** http://35.244.45.131:5000/login

---

## 🔑 Super Administrator
| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `superadmin` | `admin123` | Super Admin | Full system access, no account/team restrictions |

---

## 🏢 Account Structure & Credentials

### 🌟 Account 1: TechCorp Solutions
**Account Admin:**
| Username | Password | Role | Account | Team |
|----------|----------|------|---------|------|
| `techcorp_admin` | `admin123` | Account Admin | TechCorp Solutions | Any team in account |

#### 👥 Team 1: Development Team
**Team Admin:**
| Username | Password | Role | Account | Team |
|----------|----------|------|---------|------|
| `dev_team_admin` | `admin123` | Team Admin | TechCorp Solutions | Development Team |

**Team Members:**
| Username | Password | Role | Email | Account | Team |
|----------|----------|------|-------|---------|------|
| `john_dev` | `user123` | User | john@techcorp.com | TechCorp Solutions | Development Team |
| `sarah_dev` | `user123` | User | sarah@techcorp.com | TechCorp Solutions | Development Team |
| `mike_dev` | `user123` | User | mike@techcorp.com | TechCorp Solutions | Development Team |

#### 🔧 Team 2: Operations Team
**Team Admin:**
| Username | Password | Role | Account | Team |
|----------|----------|------|---------|------|
| `ops_team_admin` | `admin123` | Team Admin | TechCorp Solutions | Operations Team |

**Team Members:**
| Username | Password | Role | Email | Account | Team |
|----------|----------|------|---------|------|
| `lisa_ops` | `user123` | User | lisa@techcorp.com | TechCorp Solutions | Operations Team |
| `david_ops` | `user123` | User | david@techcorp.com | TechCorp Solutions | Operations Team |

---

### 🌐 Account 2: Global Innovations
**Account Admin:**
| Username | Password | Role | Account | Team |
|----------|----------|------|---------|------|
| `global_admin` | `admin123` | Account Admin | Global Innovations | Any team in account |

#### ☁️ Team 1: Cloud Infrastructure
**Team Admin:**
| Username | Password | Role | Account | Team |
|----------|----------|------|---------|------|
| `cloud_team_admin` | `admin123` | Team Admin | Global Innovations | Cloud Infrastructure |

**Team Members:**
| Username | Password | Role | Email | Account | Team |
|----------|----------|------|---------|------|
| `alex_cloud` | `user123` | User | alex@globalinnovations.com | Global Innovations | Cloud Infrastructure |
| `emma_cloud` | `user123` | User | emma@globalinnovations.com | Global Innovations | Cloud Infrastructure |
| `ryan_cloud` | `user123` | User | ryan@globalinnovations.com | Global Innovations | Cloud Infrastructure |

#### 🔒 Team 2: Security Team
**Team Admin:**
| Username | Password | Role | Account | Team |
|----------|----------|------|---------|------|
| `security_team_admin` | `admin123` | Team Admin | Global Innovations | Security Team |

**Team Members:**
| Username | Password | Role | Email | Account | Team |
|----------|----------|------|---------|------|
| `nina_security` | `user123` | User | nina@globalinnovations.com | Global Innovations | Security Team |
| `tom_security` | `user123` | User | tom@globalinnovations.com | Global Innovations | Security Team |

---

## 🎯 Login Instructions by Role

### 🔑 Super Admin Login
1. Username: `superadmin`
2. Password: `admin123`
3. **No account/team selection required** - full access to entire system

### 🏢 Account Admin Login
1. Username: `techcorp_admin` or `global_admin`
2. Password: `admin123`
3. **Select your account** from dropdown
4. **Team selection optional** - can access all teams in your account

### 👥 Team Admin Login
1. Username: `[team]_team_admin` (e.g., `dev_team_admin`)
2. Password: `admin123`
3. **Select your account** from dropdown
4. **Select your specific team** from dropdown

### 👤 Regular User Login
1. Username: `[name]_[team]` (e.g., `john_dev`)
2. Password: `user123`
3. **Select your account** from dropdown
4. **Select your specific team** from dropdown

---

## 🚀 Testing Different Access Levels

### Test Super Admin Access:
- Login: `superadmin` / `admin123`
- Should see: Full dashboard, all accounts/teams, admin panels

### Test Account Admin Access:
- Login: `techcorp_admin` / `admin123`
- Select: TechCorp Solutions account
- Should see: All teams in TechCorp Solutions, account management

### Test Team Admin Access:
- Login: `dev_team_admin` / `admin123`
- Select: TechCorp Solutions → Development Team
- Should see: Development Team data, team management

### Test Regular User Access:
- Login: `john_dev` / `user123`
- Select: TechCorp Solutions → Development Team
- Should see: Team-specific dashboard, limited access

---

## 📋 Quick Reference

| Role | Accounts | Teams | Users | Total |
|------|----------|-------|-------|-------|
| Super Admin | All | All | 1 | 1 |
| Account Admin | Own Account | All in Account | 2 | 2 |
| Team Admin | Own Account | Own Team | 4 | 4 |
| Regular User | Own Account | Own Team | 10 | 10 |
| **TOTAL** | **2** | **4** | **17** | **17** |

---

## 💡 Notes
- All passwords are consistent within role groups for easy testing
- Email addresses follow realistic corporate patterns
- Account/team selections are enforced by the authentication system
- Each user has appropriate access levels based on their role
- The system supports multi-tenant architecture with proper isolation