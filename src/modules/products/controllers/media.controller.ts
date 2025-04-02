import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  Param,
  Get,
  Delete,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { ApiTags, ApiOperation, ApiResponse, ApiConsumes } from '@nestjs/swagger'; // Agregamos los decoradores de Swagger
import { MediaService } from '../services/media.service';
import { storageConfig } from '../../../config/storage.config';

@ApiTags('media') // Define el tag "media"
@Controller('media')
export class MediaController {
  constructor(private mediaService: MediaService) {}

  @Post('upload')
  @ApiOperation({ description: 'Uploads a new media file.' })
  @ApiConsumes('multipart/form-data') // Indica que el endpoint acepta multipart/form-data
  @ApiResponse({ status: 201, description: 'Media file uploaded successfully.' })
  @UseInterceptors(FileInterceptor('file', storageConfig))
  async uploadFile(@UploadedFile() file: Express.Multer.File) {
    return await this.mediaService.Upload_Media(file);
  }

  @Get('secure-url/:media_id')
  @ApiOperation({ description: 'Retrieves a secure URL for a specific media file.' })
  @ApiResponse({ status: 200, description: 'Secure URL retrieved successfully.' })
  async getSecureFileUrl(@Param('media_id') media_id: number) {
    const url = await this.mediaService.Generate_Signed_Url(media_id);
    return { secure_url: url };
  }

  @Get('url/:media_id')
  @ApiOperation({ description: 'Retrieves a public URL for a specific media file.' })
  @ApiResponse({ status: 200, description: 'Public URL retrieved successfully.' })
  async get_Publice_File_Url(@Param('media_id') media_id: number) {
    const url = await this.mediaService.Get_Public_Url(media_id);
    return { public_url: url };
  }

  @Delete('delete/:media_id')
  @ApiOperation({ description: 'Deletes a specific media file by ID.' })
  @ApiResponse({ status: 200, description: 'Media file deleted successfully.' })
  async delete_media_file(@Param('media_id') media_id: number) {
    const rep = await this.mediaService.Delete_Media_Files(media_id);
    return rep;
  }
}