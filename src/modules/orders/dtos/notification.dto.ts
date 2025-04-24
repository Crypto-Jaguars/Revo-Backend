import { IsNotEmpty, IsEmail, IsString } from 'class-validator';

export  class notifyDto{
    @IsNotEmpty()
    @IsEmail()
    email:string;

    @IsNotEmpty()
    phone:string;

    @IsNotEmpty()
    orderId:string;
    
    @IsNotEmpty()
    status:string

}

export class EmailDto {
  @IsEmail()
  @IsNotEmpty()
  to: string;

  
  @IsString()
  @IsNotEmpty()
  subject: string;

  @IsString()
  text?: string;

  @IsString()
  @IsNotEmpty()
  html: string;
}

export class SMSDto{
    @IsEmail()
    @IsNotEmpty()
    to: string;
  
    
    @IsString()
    @IsNotEmpty()
    message: string
}