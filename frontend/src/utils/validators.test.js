// frontend/src/utils/validators.test.js
/**
 * Tests for form validators
 */

import { validators, validateField, validateForm } from "./validators";

describe("Validators", () => {
  describe("required", () => {
    it("should reject empty strings", () => {
      expect(validators.required("")).not.toBeNull();
      expect(validators.required(null)).not.toBeNull();
      expect(validators.required(undefined)).not.toBeNull();
    });

    it("should accept non-empty strings", () => {
      expect(validators.required("value")).toBeNull();
    });
  });

  describe("email", () => {
    it("should reject invalid emails", () => {
      expect(validators.email("invalid")).not.toBeNull();
      expect(validators.email("invalid@")).not.toBeNull();
      expect(validators.email("@example.com")).not.toBeNull();
    });

    it("should accept valid emails", () => {
      expect(validators.email("user@example.com")).toBeNull();
      expect(validators.email("test+tag@domain.co.uk")).toBeNull();
    });
  });

  describe("minLength", () => {
    it("should reject strings shorter than min", () => {
      const validator = validators.minLength(5);
      expect(validator("abc")).not.toBeNull();
    });

    it("should accept strings longer than min", () => {
      const validator = validators.minLength(5);
      expect(validator("abcdef")).toBeNull();
    });
  });

  describe("password", () => {
    it("should reject weak passwords", () => {
      expect(validators.password("short")).not.toBeNull();
      expect(validators.password("alllowercase123")).not.toBeNull();
      expect(validators.password("ALLUPPERCASE123")).not.toBeNull();
    });

    it("should accept strong passwords", () => {
      expect(validators.password("StrongPass123")).toBeNull();
    });
  });

  describe("numeric", () => {
    it("should reject non-numeric values", () => {
      expect(validators.numeric("abc")).not.toBeNull();
    });

    it("should accept numeric values", () => {
      expect(validators.numeric("123")).toBeNull();
      expect(validators.numeric("45.67")).toBeNull();
    });
  });

  describe("range", () => {
    it("should reject values outside range", () => {
      const validator = validators.range(1, 10);
      expect(validator("0")).not.toBeNull();
      expect(validator("11")).not.toBeNull();
    });

    it("should accept values within range", () => {
      const validator = validators.range(1, 10);
      expect(validator("5")).toBeNull();
    });
  });
});

describe("validateField", () => {
  it("should return first error from multiple validators", () => {
    const error = validateField("", [
      validators.required,
      validators.minLength(5),
    ]);
    expect(error).not.toBeNull();
  });

  it("should return null if all validators pass", () => {
    const error = validateField("validvalue", [
      validators.required,
      validators.minLength(5),
    ]);
    expect(error).toBeNull();
  });
});

describe("validateForm", () => {
  it("should validate entire form", () => {
    const formData = {
      name: "",
      email: "invalid",
      password: "weak",
    };

    const rules = {
      name: [validators.required],
      email: [validators.email],
      password: [validators.password],
    };

    const errors = validateForm(formData, rules);

    expect(errors.name).not.toBeNull();
    expect(errors.email).not.toBeNull();
    expect(errors.password).not.toBeNull();
  });

  it("should return empty object if all fields valid", () => {
    const formData = {
      name: "John",
      email: "john@example.com",
      password: "StrongPass123",
    };

    const rules = {
      name: [validators.required],
      email: [validators.email],
      password: [validators.password],
    };

    const errors = validateForm(formData, rules);

    expect(Object.keys(errors)).toHaveLength(0);
  });
});
