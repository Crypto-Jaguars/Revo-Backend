import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
} from '@nestjs/common';
import { Observable, tap } from 'rxjs';
import { ProductCache } from '../cache/product.cache';
import { Request } from 'express';

@Injectable()
export class productCacheInterceptor implements NestInterceptor {
  constructor(private readonly productCache: ProductCache) {}

  intercept(
    context: ExecutionContext,
    next: CallHandler<any>,
  ): Observable<any> | Promise<Observable<any>> {
    const request: Request = context.switchToHttp().getRequest();

    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(request.method)) {
      return next.handle().pipe(
        tap(async () => {
          if (request.params) {
            console.log('params from interceptors', request.params);
            await this.productCache.invalidateSingleProduct(request.params.id);
          }
          await this.productCache.InvalidateAll();
        }),
      );
    }
  }
}
