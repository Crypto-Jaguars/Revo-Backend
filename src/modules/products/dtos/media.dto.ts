import { IsString, IsNumber } from 'class-validator';

export class MediaResponseDTO {
  @IsNumber()
  media_id: number;

  @IsString()
  media_key: string;

  @IsString()
  format: string;

  @IsNumber()
  size: number;
}
