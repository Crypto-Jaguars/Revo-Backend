import { IsOptional, IsString } from 'class-validator';

export class UpdateCategoryDTO {
  @IsOptional()
  @IsString()
  name: string;
}
