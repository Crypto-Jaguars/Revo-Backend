import {
  IsString,
  IsNumber,
  IsOptional,
  IsArray,
  IsDate,
  IsDateString,
} from 'class-validator';

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
  @IsString({ each: true })
  @IsOptional()
  images?: string[];

  @IsNumber()
  @IsOptional()
  stockQuantity?: number;

  @IsDate()
  @IsOptional()
  harvestDate?: Date;
}

export class BulkUpdateDTO {
  @IsString()
  id: string;

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
  @IsString({ each: true })
  @IsOptional()
  images?: string[];

  @IsNumber()
  @IsOptional()
  stockQuantity?: number;

  @IsDateString()
  @IsOptional()
  harvestDate?: Date;
}
