import {
  Controller,
  Get,
  Query,
  ValidationPipe,
  BadRequestException,
  Logger,
  Inject,
} from "@nestjs/common";
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { SearchService } from "../services/search.service";
import { CombinedSearchFilterDto } from "../dtos/searchFilter.dto";
import { SearchDto } from "../dtos/search.dto";
import { FilterDto } from "../dtos/filter.dto";

@Controller("products")
export class SearchController {
  private readonly logger = new Logger(SearchController.name);

  constructor(
    private readonly searchService: SearchService,
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
  ) { }

  @Get("search")
  async searchProducts(
    @Query(new ValidationPipe({
      transform: true,
      whitelist: true,
      forbidNonWhitelisted: true,
      skipMissingProperties: false
    })) queryParams: CombinedSearchFilterDto
  ) {
    try {
      const { search, filter } = queryParams;
      const cacheKey = `search_products:${JSON.stringify({ search, filter })}`;
      const cachedResult = await this.cacheManager.get(cacheKey);
      if (cachedResult) {
        this.logger.log(`Cache hit for key: ${cacheKey}`);
        return cachedResult;
      }

      this.logSearchAnalytics(search, filter);

      if (!search?.query && !filter?.category && !filter?.minPrice && !filter?.maxPrice && !filter?.brand) {
        throw new BadRequestException("At least one search or filter parameter is required.");
      }
      const result = await this.searchService.searchProducts(search, filter);
      try {
        await this.cacheManager.set(cacheKey, result, 600); // 600 segundos (10 minutos)
      } catch (cacheError) {
        this.logger.warn(
          `Failed to set cache for key: ${cacheKey}, reason: ${cacheError.message}`
        );
      }
      this.logger.log(`Cache miss for key: ${cacheKey}, storing result`);
      return result;

    } catch (cacheError) {
      this.logger.warn(
        `Failed to set cache for key: cacheKey, reason: ${cacheError.message}`
      );
    }

  }

  private logSearchAnalytics(search?: SearchDto, filter?: FilterDto): void {
    const analyticsData = {
      timestamp: new Date().toISOString(),
      query: search?.query || null,
      filters: filter
        ? {
          category: filter.category || null,
          price: filter.minPrice || filter.maxPrice
            ? { min: filter.minPrice || null, max: filter.maxPrice || null }
            : null,
          brand: filter.brand || null,
        }
        : null,
    };

    this.logger.log(`SEARCH_ANALYTICS: ${JSON.stringify(analyticsData)}`);
  }
}