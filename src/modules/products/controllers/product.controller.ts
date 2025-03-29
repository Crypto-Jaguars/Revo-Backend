import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Put,
  Delete,
  NotFoundException,
  InternalServerErrorException,
  UseInterceptors,
} from '@nestjs/common';
import { ProductService } from '../services/product.service';
import { CreateProductDTO } from '../dtos/create-product.dto';
import { BulkUpdateDTO, UpdateProductDTO } from '../dtos/update-product.dto';
import { productCacheInterceptor } from '../interceptors/cache.interceptor';

@Controller('products')
export class ProductController {
  constructor(private readonly productService: ProductService) {}

  @UseInterceptors(productCacheInterceptor)
  @Post('/')
  async create(@Body() createProductDTO: CreateProductDTO) {
    try {
      return await this.productService.create(createProductDTO);
    } catch (error) {
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Get('/')
  async findAll() {
    try {
      return await this.productService.findAll();
    } catch (error) {
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    try {
      return await this.productService.findOne(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw error;
    }
  }

  @UseInterceptors(productCacheInterceptor)
  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() updateProductDTO: UpdateProductDTO,
  ) {
    try {
      return await this.productService.update(id, updateProductDTO);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to update product');
    }
  }

  @UseInterceptors(productCacheInterceptor)
  @Put('/bulk/update')
  async bulkUpdate(@Body() body: BulkUpdateDTO[]) {
    return await this.productService.bulkUpdate(body);
  }

  @UseInterceptors(productCacheInterceptor)
  @Delete(':id')
  async remove(@Param('id') id: string) {
    try {
      return await this.productService.remove(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to delete product');
    }
  }

  @UseInterceptors(productCacheInterceptor)
  @Delete('/softdelete/:id')
  async softDelete(@Param('id') id: string) {
    return await this.productService.softDelete(id);
  }
}
