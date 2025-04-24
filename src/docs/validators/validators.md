# **Validators Documentation**

This document provides an overview of the validators used in the application. Validators are essential for ensuring that incoming data adheres to specific rules before it is processed by the application. This helps prevent invalid data from propagating through the system, improving reliability and maintainability.

---

## **What Are Validators?**

Validators are tools or libraries used to enforce rules on data. They ensure that the data provided by users or external systems meets the expected format, type, or constraints. In this project, the `class-validator` library is used to validate Data Transfer Objects (DTOs).

---

## **Why Use Validators?**

1. **Prevent Invalid Data**:
   - Validators ensure that only valid data is passed to the service or database layers.
   - Example: Ensuring a `username` is a non-empty string.

2. **Improve Code Reliability**:
   - By validating data at the entry point, runtime errors caused by invalid data are minimized.

3. **Simplify Validation Logic**:
   - Validators move validation logic out of the business logic, making the code cleaner and easier to maintain.

4. **Enhance Security**:
   - Validators help prevent malicious or malformed data from being processed, reducing vulnerabilities.

---

## **Validators Used in This Project**

This project uses the `class-validator` library to validate DTOs. Below are some of the commonly used decorators:

| Decorator       | Description                                      | Example Usage                          |
|------------------|--------------------------------------------------|----------------------------------------|
| `@IsNotEmpty`   | Ensures the field is not empty.                  | `@IsNotEmpty() username: string;`      |
| `@IsString`     | Ensures the field is a string.                   | `@IsString() description: string;`     |
| `@IsNumber`     | Ensures the field is a number.                   | `@IsNumber() price: number;`           |
| `@IsOptional`   | Marks the field as optional.                     | `@IsOptional() images?: string[];`     |
| `@IsArray`      | Ensures the field is an array.                   | `@IsArray() tags: string[];`           |
| `@IsDate`       | Ensures the field is a valid date.               | `@IsDate() createdAt: Date;`           |

---

## **Examples of Validators in DTOs**

### **1. LoginDto**
The `LoginDto` validates the data required for user login.

**Code Example**:
```typescript
import { IsNotEmpty, IsString } from 'class-validator';

export class LoginDto {
  @IsNotEmpty()
  @IsString()
  username: string;

  @IsNotEmpty()
  @IsString()
  password: string;
}
```

### **2. UpdateProductDTO**
The `UpdateProductDTO` validates the data required for updating a product.

**Code Example**:
```typescript
import { IsString, IsNumber, IsOptional, IsArray, IsDate } from 'class-validator';

export class UpdateProductDTO {
  @IsString()
  @IsOptional()
  name?: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsNumber()
  @IsOptional()
  price?: number;

  @IsString()
  @IsOptional()
  unit?: string;

  @IsArray()
  @IsOptional()
  images?: string[];

  @IsNumber()
  @IsOptional()
  stockQuantity?: number;

  @IsDate()
  @IsOptional()
  harvestDate?: Date;
}
```
## **How Validators Are Used in the Application**
### **1. Validation in Controllers:**

DTOs with validation decorators are used in controller methods to validate incoming requests.

**Usage Example**:
```typescript
@Post('login')
login(@Body() loginDto: LoginDto) {
  // loginDto is automatically validated
  return this.authService.login(loginDto);
}
```



### **2. Custom Validator: IsPositiveConstraint**
The `IsPositiveConstraint` is a custom validator that ensures a value is positive.

**Code Example**:
```typescript
import { ValidatorConstraint, ValidatorConstraintInterface, ValidationArguments } from 'class-validator';

@ValidatorConstraint({ name: 'isPositive', async: false })
export class IsPositiveConstraint implements ValidatorConstraintInterface {
  validate(value: number, args: ValidationArguments) {
    return value > 0; // Value must be positive
  }

  defaultMessage(args: ValidationArguments) {
    return 'Value must be a positive number!';
  }
}
```

### **3. Global Validation Pipe**
The `ValidationPipe` is used globally to validate all incoming requests.

**Code Example**:
```typescript
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(new ValidationPipe());
  await app.listen(3000);
}
bootstrap();
```