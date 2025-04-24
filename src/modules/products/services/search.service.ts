import { Injectable, InternalServerErrorException, Logger } from '@nestjs/common';
import { ProductRepository } from '../repositories/product.repository';
import { SearchDto } from '../dtos/search.dto';
import { FilterDto } from '../dtos/filter.dto';

@Injectable()
export class SearchService {
  private readonly logger = new Logger(SearchService.name);

  constructor(private readonly productRepository: ProductRepository) {}

  async searchProducts(searchDto: SearchDto, filterDto: FilterDto) {
    try {
      const { query } = searchDto;

     
      if (query) {
        this.logger.log(`User searched for: ${query}`);
      }

      this.logger.log(
        `Executing product search with: ${JSON.stringify(searchDto)}, ${JSON.stringify(filterDto)}`
      );

      return await this.productRepository.searchProducts(searchDto, filterDto);
    } catch (error) {
      this.logger.error('Failed to fetch products', error.stack);
      throw new InternalServerErrorException('Something went wrong while fetching products.');
    }
  }
}
