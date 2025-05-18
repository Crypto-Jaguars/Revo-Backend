import { IsString, IsNumber, IsOptional, IsBoolean, IsArray, IsDateString, IsEnum, Length, Min, IsUUID } from 'class-validator';
import { Transform } from 'class-transformer';

export class CreateProductDto {
  @IsString()
  @Length(1, 255)
  name: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsNumber({ maxDecimalPlaces: 2 })
  @Min(0)
  @Transform(({ value }) => parseFloat(value))
  price: number;

  @IsString()
  @Length(1, 50)
  priceUnit: string;

  @IsUUID()
  @IsString()
  farmerId: string;

  @IsString()
  @Length(1, 100)
  category: string;

  @IsOptional()
  @IsString()
  @Length(1, 100)
  subCategory?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];

  @IsNumber()
  @Min(0)
  @Transform(({ value }) => parseInt(value))
  stockQuantity: number;

  @IsOptional()
  @IsDateString()
  @Transform(({ value }) => value ? new Date(value) : undefined)
  harvestDate?: Date;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  certifications?: string[];

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  seasonality?: string[];

  @IsOptional()
  @IsString()
  @Length(1, 50)
  farmingMethod?: string;

  @IsOptional()
  @IsBoolean()
  @Transform(({ value }) => value === 'true' || value === true)
  availableForDelivery?: boolean;

  @IsOptional()
  @IsBoolean()
  @Transform(({ value }) => value === 'true' || value === true)
  pickupAvailable?: boolean;
}