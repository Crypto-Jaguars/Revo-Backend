// src/modules/products/product.controller.ts
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
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ProductService } from '../services/product.service';
import { CreateProductDTO } from '../dtos/create-product.dto';
import { UpdateProductDTO } from '../dtos/update-product.dto';
import { ProductSchema } from '../../../docs/schemas/schemas';

@ApiTags('products')
@Controller('products')
export class ProductController {
  constructor(private readonly productService: ProductService) {}

  @Post()
  @ApiOperation({ description: 'Creates a new product in the marketplace.' })
  @ApiResponse({ status: 201, description: 'The product has been successfully created.', type: ProductSchema })
  @ApiResponse({ status: 404, description: 'Not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async create(@Body() createProductDTO: CreateProductDTO) {
    try {
      return await this.productService.create(createProductDTO);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Get()
  @ApiOperation({ description: 'Retrieves a list of all products.' })
  @ApiResponse({ status: 200, description: 'List of products retrieved successfully.', type: [ProductSchema] })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
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
  @ApiOperation({ description: 'Retrieves a specific product by ID.' })
  @ApiResponse({ status: 200, description: 'Product retrieved successfully.', type: ProductSchema })
  @ApiResponse({ status: 404, description: 'Product not found.' })
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

  @Put(':id')
  @ApiOperation({ description: 'Updates a specific product by ID.' })
  @ApiResponse({ status: 200, description: 'Product updated successfully.', type: ProductSchema })
  @ApiResponse({ status: 404, description: 'Product not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
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

  @Delete(':id')
  @ApiOperation({ description: 'Deletes a specific product by ID.' })
  @ApiResponse({ status: 200, description: 'Product deleted successfully.' })
  @ApiResponse({ status: 404, description: 'Product not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
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
}