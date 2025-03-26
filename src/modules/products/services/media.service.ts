import { Injectable, BadRequestException } from '@nestjs/common';
import { S3, GetObjectCommand } from '@aws-sdk/client-s3';
import { ConfigService } from '@nestjs/config';
import { ProductImage } from '../entities/product-image.entity';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';
import { MediaResponseDTO } from '../dtos/media.dto';
import { createReadStream } from 'fs';
import { unlink } from 'fs/promises';
import sharp from 'sharp';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

@Injectable()
export class MediaService {
  private S3_client: S3;

  constructor(
    private configService: ConfigService,
    @InjectRepository(ProductImage)
    private readonly ProductImageRepo: Repository<ProductImage>,
  ) {
    this.S3_client = new S3({
      endpoint: process.env.S3_ENDPOINT_URL,
      region: process.env.AWS_REGION,
      credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      },
      forcePathStyle: true, // Required for LocalStack / MinIO
    });
  }

  async Upload_Media(file: Express.Multer.File): Promise<MediaResponseDTO> {
    try {
      // Validate file input
      if (!file || !file.path || !file.originalname) {
        throw new BadRequestException('Invalid_file_input');
      }

      const fileKey = `media/${Date.now()}-${file.originalname}`;
      let file_data = null;
      const isImage = file.mimetype.startsWith('image/');

      if (isImage) {
        // Processing image before uploading OKK!
        file_data = await this.optimizeImage(file);
      } else {
        file_data = file.path;
      }

      // Upload file to AWS S3 OKK!!
      await this.upload_AWS(fileKey, file_data, file.mimetype, isImage);
      console.log('File uploaded to S3:', fileKey);

      // Save file details to DB OKK!
      const savedMedia = await this.ProductImageRepo.save(
        this.ProductImageRepo.create({
          media_key: fileKey,
          format: file.mimetype,
          size: file.size,
        }),
      );

      // delete  local file after upload OKK !

      await unlink(file.path);

      return savedMedia;
    } catch (error) {
      throw new BadRequestException(
        `Failed_to_process_or_upload_file: ${error.message}`,
      );
    }
  }

  async generateSignedUrl(file_id: number): Promise<string> {
    try {
      if (!file_id) {
        throw new BadRequestException('file_id is required');
      }

      const fileRecord = await this.ProductImageRepo.findOne({
        where: { media_id: file_id },
      });

      if (!fileRecord) {
        throw new BadRequestException('File_not_found');
      }

      const command = new GetObjectCommand({
        Bucket: process.env.AWS_BUCKET_NAME,
        Key: fileRecord.media_key,
      });

      const signedUrl = await getSignedUrl(this.S3_client, command, {
        expiresIn: 3600,
      });
      return signedUrl;
    } catch (error) {
      throw new BadRequestException(
        `Failed to generate secure URL: ${error.message}`,
      );
    }
  }

  private async optimizeImage(file: Express.Multer.File): Promise<Buffer> {
    try {
      const ext = file.mimetype.split('/')[1];
      return await sharp(file.path)
        .resize(800)
        [ext]({ quality: 80 })
        .toBuffer();
    } catch (e) {
      throw new BadRequestException(`error_optimizing_image: ${e.message}`);
    }
  }

  private async upload_AWS(
    fileKey: string,
    file_data: Buffer | string,
    mimeType: string,
    isImage: boolean,
  ) {
    try {
      let body;
      if (isImage) {
        body = file_data as Buffer;
      } else {
        body = createReadStream(file_data as string);
      }

      await this.S3_client.putObject({
        Bucket: process.env.AWS_BUCKET_NAME,
        Key: fileKey,
        Body: body,
        ContentType: mimeType,
      });
    } catch (e) {
      throw new BadRequestException('Error_uploading_file_to_AWS', e);
    }
  }
}
