import {
  BadRequestException,
  Injectable,
  InternalServerErrorException,
  NotFoundException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Category } from '../entities/category.entity';
import { Repository } from 'typeorm';
import { UpdateCategoryDTO } from '../dtos/update-category.dto';
import { CreateCategoryDTO } from '../dtos/create-category.dto';
import { Product } from '../entities/product.entity';

@Injectable()
export class CategoryService {
  constructor(
    @InjectRepository(Category)
    private readonly categoryRepository: Repository<Category>,
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
  ) {}

  async findAll(): Promise<Category[]> {
    try {
      return await this.categoryRepository.find();
    } catch (error) {
      throw new InternalServerErrorException('Failed to fetch categories');
    }
  }

  async findOne(id: string): Promise<Category> {
    const category = await this.categoryRepository.findOne({ where: { id } });
    if (!category) {
      throw new NotFoundException(`Category with ID ${id} not found`);
    }
    return category;
  }

  async create(createCategoryDTO: CreateCategoryDTO): Promise<Category> {
    try {
      const category = await this.categoryRepository.create(createCategoryDTO);
      return await this.categoryRepository.save(category);
    } catch (error) {
      throw new BadRequestException('Failed to create category');
    }
  }

  async update(
    id: string,
    updateCategoryDTO: UpdateCategoryDTO,
  ): Promise<Category> {
    try {
      const category = await this.categoryRepository.findOne({ where: { id } });
      if (!category) {
        throw new NotFoundException(`Category with ID ${id} not found`);
      }
      Object.assign(category, updateCategoryDTO);
      return await this.categoryRepository.save(category);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw new InternalServerErrorException('Failed to update category');
    }
  }

  async remove(id: string): Promise<void> {
    try {
      const category = await this.findOne(id);

      const productsAssociated = await this.productRepository.find({
        where: { category: { id: category.id } }, // Query the category relationship
      });

      if (productsAssociated.length > 0) {
        throw new BadRequestException(
          'Category has products associated with it',
        );
      }

      await this.categoryRepository.softDelete(category.id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      if (error instanceof BadRequestException) {
        throw error;
      }
      throw new InternalServerErrorException('Failed to delete category');
    }
  }
}