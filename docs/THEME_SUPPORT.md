# Light/Dark Theme Support

## Overview

ADF Monitor Pro now features comprehensive **Light/Dark theme support**, providing users with the flexibility to choose their preferred visual experience. The theme system includes custom styling for all components, ensuring optimal readability and visual appeal in both modes.

## Features

### 🎨 **Theme Selector**
- **Location**: Top of the sidebar in "Control Center"
- **Options**: Light Theme, Dark Theme
- **Toggle**: Horizontal radio buttons for easy switching
- **Persistence**: Theme preference is maintained throughout the session

### 🌞 **Light Theme**
Perfect for daytime use and well-lit environments:

#### Visual Characteristics:
- **Primary Background**: Clean white (#ffffff)
- **Text Color**: Dark gray (#1a202c) for excellent readability
- **Accent Colors**: Professional blues (#4299e1, #3182ce)
- **Card Styling**: Subtle shadows with light borders
- **Button Hovers**: Smooth transitions with elevation effects

#### Components:
- **Header**: Blue gradient with white text and shadow
- **Metric Cards**: White backgrounds with blue accents and light borders
- **Environment Cards**: 
  - 🔴 **Production**: Light red background with red borders
  - 🟡 **Staging**: Light orange background with orange borders  
  - 🟢 **Development**: Light green background with green borders
- **Sidebar**: Light gray sections with subtle borders
- **Alerts**: Bright, clear color coding for easy identification

### 🌙 **Dark Theme**
Optimal for low-light environments and reduced eye strain:

#### Visual Characteristics:
- **Primary Background**: Deep dark blue (#0e1117)
- **Text Color**: Off-white (#fafafa) for comfortable reading
- **Accent Colors**: Bright blues for contrast
- **Card Styling**: Dark backgrounds with colored borders
- **Enhanced Shadows**: Deeper shadows for better depth perception

#### Components:
- **Header**: Dark gradient with bright text and strong shadows
- **Metric Cards**: Dark blue backgrounds with colored accents
- **Environment Cards**:
  - 🔴 **Production**: Dark red background with red accents
  - 🟡 **Staging**: Dark orange background with orange accents
  - 🟢 **Development**: Dark green background with green accents  
- **Sidebar**: Dark sections with subtle gray borders
- **Enhanced Contrast**: Optimized colors for dark mode visibility

### ✨ **Theme-Aware Components**

#### Multi-Environment Dashboard:
- **Environment Health Cards**: Automatically styled based on theme
- **Metric Containers**: Proper contrast and readability in both themes
- **Status Indicators**: Clear visibility regardless of theme choice

#### Failure Analysis Page:
- **Environment-Specific Cards**: Color-coded backgrounds that work in both themes
- **Filter Components**: Styled for optimal usability
- **Expandable Sections**: Proper contrast and borders

#### Interactive Elements:
- **Buttons**: Hover effects and transitions optimized for each theme
- **Dropdowns**: Styled borders and backgrounds
- **Alerts**: Color schemes that maintain meaning across themes

## Technical Implementation

### CSS Architecture:
```css
/* Theme-specific styling approach */
.stApp {
    background-color: [theme-specific-color];
    color: [theme-specific-text-color];
}

/* Environment-aware classes */
.environment-prod { /* Production styling */ }
.environment-staging { /* Staging styling */ }
.environment-dev { /* Development styling */ }

/* Component-specific classes */
.metric-container { /* Metric card styling */ }
.main-header { /* Header styling */ }
.sidebar-section { /* Sidebar styling */ }
```

### Session State Management:
```python
# Theme persistence
if 'ui_theme' not in st.session_state:
    st.session_state.ui_theme = 'Dark'

# Dynamic theme application
def apply_theme_styling():
    theme = st.session_state.get('ui_theme', 'Dark')
    if theme == 'Light':
        # Apply light theme CSS
    else:
        # Apply dark theme CSS
```

### Component Integration:
- **Environment Cards**: Use CSS classes instead of inline styles
- **Dynamic Styling**: Theme applied on every page load
- **Responsive Design**: Works across different screen sizes

## User Experience Benefits

### 🔆 **Light Theme Advantages**:
- **Professional Appearance**: Clean, corporate-friendly design
- **High Contrast**: Excellent readability in bright environments  
- **Print Friendly**: Works well for printed reports and documentation
- **Classic Feel**: Familiar interface for traditional applications

### 🌑 **Dark Theme Advantages**:
- **Reduced Eye Strain**: Easier on the eyes during extended use
- **Battery Efficient**: Lower power consumption on OLED displays
- **Modern Aesthetic**: Contemporary, developer-friendly appearance
- **Focus Enhancement**: Reduces distractions with darker backgrounds

### 🔄 **Seamless Switching**:
- **Instant Change**: Theme applies immediately upon selection
- **No Data Loss**: All content and state preserved during switch
- **Visual Continuity**: Consistent layouts across both themes
- **Accessibility**: Better options for users with visual preferences

## Usage Instructions

### Switching Themes:
1. **Navigate** to any page in the application
2. **Locate** the "🎨 Theme" section in the sidebar
3. **Select** your preferred theme (Light/Dark) 
4. **Experience** the instant visual transformation

### Best Practices:
- **Daytime Use**: Light theme for better visibility in bright environments
- **Evening Use**: Dark theme to reduce eye strain
- **Team Demos**: Light theme for presentations and meetings
- **Extended Monitoring**: Dark theme for long monitoring sessions

## Customization Potential

### Future Enhancements:
- **Custom Color Schemes**: User-defined accent colors
- **Environment-Specific Themes**: Different themes per environment
- **Auto Theme Switching**: Time-based theme changes
- **High Contrast Mode**: Enhanced accessibility options
- **Color Blind Support**: Alternative color palettes

### Configuration Options:
- **Default Theme Setting**: Admin-configurable default
- **User Preferences**: Persistent theme choices per user
- **Team Standards**: Organization-wide theme policies

## Accessibility Features

### Light Theme Accessibility:
- **WCAG Compliant**: High contrast ratios for readability
- **Color Coding**: Multiple visual cues beyond just color
- **Clear Borders**: Well-defined component boundaries
- **Readable Fonts**: Optimized text contrast

### Dark Theme Accessibility:
- **Reduced Glare**: Comfortable viewing in low light
- **Enhanced Contrast**: Bright text on dark backgrounds
- **Visual Hierarchy**: Clear information organization
- **Focus Indicators**: Visible interactive element highlighting

## Getting Started

1. **Launch** ADF Monitor Pro at `http://localhost:8501`
2. **Look** for the "🎨 Theme" section in the left sidebar
3. **Choose** between Light and Dark theme options
4. **Explore** all features in your preferred visual mode
5. **Switch** themes anytime to compare the experience

The theme system is designed to enhance user experience while maintaining all functionality and features across both visual modes. Choose the theme that best fits your working environment and personal preferences! 🎨✨