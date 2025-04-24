import { IsOptional, IsString, IsNumber, IsEnum, Min, ValidateNested } from "class-validator";
import { Type } from "class-transformer";
import { SearchDto } from "./search.dto";
import { FilterDto } from "./filter.dto";

export class CombinedSearchFilterDto {
  @IsOptional()
  @ValidateNested()
  @Type(() => SearchDto)
  search?: SearchDto;

  @IsOptional()
  @ValidateNested()
  @Type(() => FilterDto)
  filter?: FilterDto;
}
