# **Enums in TypeScript**

Enums (short for "enumerations") are a feature in TypeScript that allows you to define a set of named constants. They are used to represent a fixed set of related values, making your code more readable, maintainable, and type-safe.

---

## **Purpose of Enums**

Enums are used to:
1. **Group Related Constants**: Enums allow you to group related constants under a single name, making your code more organized.
2. **Improve Code Readability**: By using descriptive names for constants, enums make your code easier to understand.
3. **Ensure Type Safety**: Enums restrict values to a predefined set, reducing the risk of invalid values being used.
4. **Provide Runtime Representation**: Unlike TypeScript types, enums are compiled into JavaScript and can be used at runtime.

---

## **Types of Enums**

### **1. Numeric Enums**
Numeric enums are the default in TypeScript. Each member of the enum is assigned a numeric value, starting from `0` by default.

**Example:**
```typescript
export enum UserRole {
  ADMIN = 1,
  USER = 2,
  GUEST = 3,
}

const role: UserRole = UserRole.ADMIN;
console.log(role); // Output: 0
```

### **2. String Enums**
String enums are enums where each member is assigned a string value.

**Example:**
```typescript
export enum OrderStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  CANCELED = 'canceled',
}

const status: OrderStatus = OrderStatus.PENDING;
console.log(status); // Output: 'pending'
```