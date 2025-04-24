/* eslint-disable prettier/prettier */
import { IsOptional, IsDateString } from 'class-validator';

export class ReportExportDto {
  @IsOptional()
  @IsDateString()
  startDate?: string;

  @IsOptional()
  @IsDateString()
  endDate?: string;
}
