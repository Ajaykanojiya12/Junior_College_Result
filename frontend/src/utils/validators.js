// src/utils/validators.js

/**
 * Validation functions for form inputs
 */

export const validators = {
  /**
   * Validate if a string is not empty
   */
  required: (value) => {
    if (!value || value.toString().trim() === "") {
      return "This field is required";
    }
    return null;
  },

  /**
   * Validate email format
   */
  email: (value) => {
    if (!value) return null;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return "Invalid email format";
    }
    return null;
  },

  /**
   * Validate minimum length
   */
  minLength: (min) => (value) => {
    if (!value) return null;
    if (value.length < min) {
      return `Must be at least ${min} characters`;
    }
    return null;
  },

  /**
   * Validate maximum length
   */
  maxLength: (max) => (value) => {
    if (!value) return null;
    if (value.length > max) {
      return `Must be at most ${max} characters`;
    }
    return null;
  },

  /**
   * Validate password strength
   */
  password: (value) => {
    if (!value) return null;
    
    const errors = [];
    if (value.length < 6) errors.push("at least 6 characters");
    if (!/[A-Z]/.test(value)) errors.push("one uppercase letter");
    if (!/[a-z]/.test(value)) errors.push("one lowercase letter");
    if (!/[0-9]/.test(value)) errors.push("one number");
    
    if (errors.length > 0) {
      return `Password must contain ${errors.join(", ")}`;
    }
    return null;
  },

  /**
   * Validate that two fields match
   */
  match: (otherValue, fieldName) => (value) => {
    if (!value || !otherValue) return null;
    if (value !== otherValue) {
      return `${fieldName} does not match`;
    }
    return null;
  },

  /**
   * Validate numeric value
   */
  numeric: (value) => {
    if (!value) return null;
    if (isNaN(value)) {
      return "Must be a number";
    }
    return null;
  },

  /**
   * Validate number range
   */
  range: (min, max) => (value) => {
    if (!value) return null;
    const num = parseFloat(value);
    if (isNaN(num)) return "Must be a number";
    if (num < min || num > max) {
      return `Must be between ${min} and ${max}`;
    }
    return null;
  },

  /**
   * Custom validation function
   */
  custom: (validatorFn) => validatorFn,
};

/**
 * Run multiple validators on a value
 */
export const validateField = (value, validators) => {
  for (let validator of validators) {
    const error = validator(value);
    if (error) {
      return error;
    }
  }
  return null;
};

/**
 * Validate entire form
 */
export const validateForm = (formData, rules) => {
  const errors = {};
  
  for (const [fieldName, fieldValidators] of Object.entries(rules)) {
    const value = formData[fieldName];
    const error = validateField(value, fieldValidators);
    if (error) {
      errors[fieldName] = error;
    }
  }
  
  return errors;
};
