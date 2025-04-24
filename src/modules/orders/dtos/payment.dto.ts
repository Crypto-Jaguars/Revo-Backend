import { IsNotEmpty, IsNumber, IsString, IsPositive } from 'class-validator';

export class PaymentDto {
  @IsNotEmpty()
  @IsNumber()
  userId: number;

  @IsNotEmpty()
  @IsNumber()
  orderId: number;

  @IsNotEmpty()
  @IsPositive()
  amount: number;

  @IsNotEmpty()
  @IsString()
  currency: string;
}