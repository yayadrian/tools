# HTML/JS Tools Agent Plan

## Overview
Plans and workflows for creating and maintaining HTML/JavaScript tools in this repository.

## Creating a New HTML/JS Tool

### Step 1: Setup
1. Create a new directory for the tool
2. Create `index.html` file
3. Set up basic HTML structure

### Step 2: HTML Structure
1. Add semantic HTML elements
2. Include proper labels for all inputs
3. Set up form structure if needed
4. Ensure proper focus order

### Step 3: CSS Styling
1. Start with `*{box-sizing:border-box}` reset
2. Set inputs and textareas to 16px font size
3. Use system font fallbacks (Helvetica preferred)
4. Keep styling minimal and inline
5. Use two-space indentation

### Step 4: JavaScript
1. Start with `<script type="module">` (not indented)
2. Use modern ES6+ syntax
3. Keep functions small and focused
4. Handle user interactions
5. Implement core functionality

### Step 5: Testing
1. Test in browser
2. Verify accessibility (keyboard navigation, labels)
3. Test on different screen sizes if needed
4. Verify functionality works as expected

### Step 6: Documentation
1. Add usage comments at top if needed
2. Create README.md if tool needs explanation
3. Include examples of usage

## Updating Existing HTML/JS Tools

1. Review current implementation
2. Identify changes needed
3. Maintain single-file structure where possible
4. Update following all style rules
5. Test accessibility and functionality
6. Update documentation if behavior changes

## Common Patterns

### Form Handling
- Use proper form elements
- Include labels for all inputs
- Handle form submission
- Provide clear feedback

### File Downloads
- Render live preview when possible
- Provide download link
- Use Blob API for file generation
- Handle browser compatibility

### Data Display
- Use semantic HTML for data
- Format data clearly
- Provide clear visual hierarchy
- Ensure responsive design

### Interactive Elements
- Use appropriate event listeners
- Provide visual feedback
- Handle edge cases gracefully
- Maintain accessibility

## Accessibility Checklist

- [ ] All inputs have labels
- [ ] Focus order is logical
- [ ] Keyboard navigation works
- [ ] Semantic HTML used
- [ ] ARIA labels where needed
- [ ] Color contrast is sufficient
- [ ] Interactive elements are keyboard accessible

