import {
  Injectable,
  NotFoundException,
  InternalServerErrorException,
  BadRequestException,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Product } from '../entities/product.entity';
import { CreateProductDTO } from '../dtos/create-product.dto';
import { BulkUpdateDTO, UpdateProductDTO } from '../dtos/update-product.dto';

import {
  convertMinuteToMilleSeconds,
  convertSecondToMilleSeconds,
} from 'src/shared/utilities/conversions';
import { ConfigService } from '@nestjs/config';
import { ProductCache } from '../cache/product.cache';
import { cachedKeys } from '../constants/cache.constant';

@Injectable()
export class ProductService {
  constructor(
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
    private readonly configService: ConfigService,
    private readonly productCache: ProductCache,
  ) {}

  async create(createProductDTO: CreateProductDTO): Promise<Product> {
    try {
      const product = this.productRepository.create(createProductDTO);
      return await this.productRepository.save(product);
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      throw new BadRequestException('Failed to create product');
    }
  }

  async findAll(): Promise<Product[]> {
    try {
      const cachedResult = await this.productCache.getAllProductsFromCache();
      console.log('all products', cachedResult);
      if (cachedResult != null) {
        return cachedResult;
      }
      const result = await this.productRepository.find();
      if (result.length) {
        await this.productCache.cacheAllProducts(
          result,
          convertMinuteToMilleSeconds(
            this.configService.get<number>('ALL_PRODUCT_TTL_IN_MIN'),
          ),
        );
        return result;
      } else {
        return [];
      }

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      console.log(error);
      throw new InternalServerErrorException('Failed to fetch products');
    }
  }

  async findOne(id: string): Promise<Product> {
    // check in cache for single product
    const productKey = `${cachedKeys.SINGLE_PRODUCT}_${id}`;
    const cachedProduct =
      await this.productCache.getSingleProductFromCache(productKey);
    if (cachedProduct != null) {
      return cachedProduct[0];
    }

    // check all products cache
    const allCachedProducts: Product[] =
      await this.productCache.getAllProductsFromCache();
    if (allCachedProducts != null) {
      const product = allCachedProducts.find((p) => p.id == id);
      if (product) {
        await this.productCache.cacheSingleProduct(
          productKey,
          product,
          convertSecondToMilleSeconds(30),
        );
        return product;
      }
    }

    // if not found in cache, check db and then cache product
    const product = await this.productRepository.findOne({ where: { id } });
    if (product) {
      await this.productCache.cacheSingleProduct(
        productKey,
        product,
        convertSecondToMilleSeconds(
          this.configService.get<number>('SINGLE_PRODUCT_TTL_IN_SEC)'),
        ),
      );
      return product;
    }
    if (!product) {
      throw new NotFoundException(`Product with ID ${id} not found`);
    }
    return product;
  }

  async update(
    id: string,
    updateProductDTO: UpdateProductDTO,
  ): Promise<Product> {
    try {
      const product = await this.productRepository.findOne({ where: { id } });
      if (!product) {
        throw new NotFoundException(`Product with ID ${id} not found`);
      }
      Object.assign(product, updateProductDTO);
      return await this.productRepository.save(product);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw new InternalServerErrorException('Failed to update product');
    }
  }

  async remove(id: string): Promise<void> {
    try {
      const result = await this.productRepository.softDelete(id);
      if (result.affected === 0) {
        throw new NotFoundException(`Product with ID ${id} not found`);
      }
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw new InternalServerErrorException('Failed to delete product');
    }
  }

  async bulkUpdate(updates: BulkUpdateDTO[]) {
    const fieldGroups = this.arrangeProductFields(updates);

    await this.productRepository.manager.transaction(async (tx) => {
      try {
        for (const [field, updateValue] of Object.entries(fieldGroups)) {
          const ids = updateValue.map((val) => val.id);
          const values = updateValue.map((val) => val.value);

          if (field != 'id') {
            let setExpression: string;
            if (field === 'images') {
              setExpression = `jsonb_build_array(${values.map((value) => `'${value}'`).join(', ')})`;
            } else if (field === 'price' || field === 'stockQuantity') {
              setExpression = `CASE id ${ids.map((id, index) => `WHEN '${id}' THEN ${values[index]}`).join(' ')} END`;
            } else if (field === 'harvestDate') {
              setExpression = `CASE id ${ids.map((id, index) => `WHEN '${id}' THEN '${values[index]}'::timestamp`).join(' ')} END`;
            } else {
              setExpression = `CASE id ${ids.map((id, index) => `WHEN '${id}' THEN '${values[index]}'`).join(' ')} END`;
            }

            await tx
              .createQueryBuilder()
              .update(Product)
              .set({
                [field]: () => setExpression,
                updatedAt: () => 'CURRENT_TIMESTAMP',
              })
              .whereInIds(ids)
              .execute();
          }
        }
      } catch (err) {
        console.log(err);
        throw new InternalServerErrorException('Error completing bulk updates');
      }
    });
  }

  arrangeProductFields(data: BulkUpdateDTO[]) {
    return data.reduce(
      (acc, eachProduct) => {
        Object.entries(eachProduct).forEach(([key, value]) => {
          if (!acc[key]) {
            acc[key] = [];
          }

          acc[key].push({ id: eachProduct.id, value });
        });
        return acc;
      },
      {} as Record<string, Array<{ id: string; value: string }>>,
    );
  }

  async bulkInserts(products: CreateProductDTO[]) {
    try {
      await this.productRepository
        .createQueryBuilder()
        .insert()
        .into(Product)
        .values(products)
        .execute();
    } catch (err) {
      console.log(err);
      throw new InternalServerErrorException('error carrying out bulk inserts');
    }
  }

  async softDelete(id: string) {
    try {
      const product = await this.productRepository.findOne({ where: { id } });
      if (!product) {
        throw new NotFoundException('Product does not exist');
      }
      await this.productRepository.update(id, { deletedAt: new Date() });
    } catch (err) {
      console.log(err);
      if (
        err instanceof HttpException &&
        err.getStatus() == HttpStatus.NOT_FOUND
      ) {
        throw err;
      }
      throw new InternalServerErrorException('error carrying out soft deletes');
    }
  }
}
