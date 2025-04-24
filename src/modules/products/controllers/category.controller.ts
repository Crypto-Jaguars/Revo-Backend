import {
  BadRequestException,
  Body,
  Controller,
  Delete,
  Get,
  InternalServerErrorException,
  NotFoundException,
  Param,
  Post,
  Put,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger'; // Agregamos los decoradores de Swagger
import { CategoryService } from '../services/category.service';
import { CreateCategoryDTO } from '../dtos/create-category.dto';
import { UpdateCategoryDTO } from '../dtos/update-category.dto';

@ApiTags('categories') // Define el tag "categories"
@Controller('categories')
export class CategoryController {
  constructor(private readonly categoryService: CategoryService) {}

  @Get()
  @ApiOperation({ description: 'Retrieves a list of all categories.' })
  @ApiResponse({ status: 200, description: 'List of categories retrieved successfully.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async getAll() {
    try {
      return await this.categoryService.findAll();
    } catch (error) {
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Get(':id')
  @ApiOperation({ description: 'Retrieves a specific category by ID.' })
  @ApiResponse({ status: 200, description: 'Category retrieved successfully.' })
  @ApiResponse({ status: 404, description: 'Category not found.' })
  async findOne(@Param('id') id: string) {
    try {
      return await this.categoryService.findOne(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw error;
    }
  }

  @Post()
  @ApiOperation({ description: 'Creates a new category.' })
  @ApiResponse({ status: 201, description: 'Category created successfully.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async create(@Body() createCategoryDTO: CreateCategoryDTO) {
    try {
      return await this.categoryService.create(createCategoryDTO);
    } catch (error) {
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Put(':id')
  @ApiOperation({ description: 'Updates a specific category by ID.' })
  @ApiResponse({ status: 200, description: 'Category updated successfully.' })
  @ApiResponse({ status: 404, description: 'Category not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async update(
    @Param('id') id: string,
    @Body() updateCategoryDTO: UpdateCategoryDTO,
  ) {
    try {
      return await this.categoryService.update(id, updateCategoryDTO);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to update category');
    }
  }

  @Delete(':id')
  @ApiOperation({ description: 'Deletes a specific category by ID.' })
  @ApiResponse({ status: 200, description: 'Category deleted successfully.' })
  @ApiResponse({ status: 404, description: 'Category not found.' })
  @ApiResponse({ status: 400, description: 'Bad request.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async remove(@Param('id') id: string) {
    try {
      return await this.categoryService.remove(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      if (error instanceof BadRequestException) {
        throw new BadRequestException(error.message);
      }
      throw new InternalServerErrorException('Failed to delete category');
    }
  }
}