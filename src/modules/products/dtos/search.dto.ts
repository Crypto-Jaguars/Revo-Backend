import { IsOptional, IsString, IsEnum, IsNumber, Min } from "class-validator";
import { Transform } from "class-transformer";

export class SearchDto {
  @IsOptional()
  @IsString()
  query?: string;

  @IsOptional()
  @IsString()
  sortBy?: string;

  @IsOptional()
  @IsEnum(["ASC", "DESC"], { message: "order must be 'ASC' or 'DESC'" })
  order?: "ASC" | "DESC";

  @IsOptional()
  @Transform(({ value }) => parseInt(value, 10))
  @IsNumber()
  @Min(1)
  page?: number;

  @IsOptional()
  @Transform(({ value }) => parseInt(value, 10))
  @IsNumber()
  @Min(1)
  limit?: number;

  @IsOptional()
  @IsString()
  fields?: string;
}
