import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ProductsService } from './products.service';
import { Product } from './entities/product.entity';

describe('ProductsService', () => {
  let service: ProductsService;
  let repository: Repository<Product>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ProductsService,
        {
          provide: getRepositoryToken(Product),
          useClass: Repository,
        },
      ],
    }).compile();

    service = module.get<ProductsService>(ProductsService);
    repository = module.get<Repository<Product>>(getRepositoryToken(Product));
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('create', () => {
    it('should create and return a product', async () => {
      const dto = { name: 'Test Product', price: 100 };
      const createdProduct = { id: 1, ...dto };

      jest.spyOn(repository, 'create').mockReturnValue(createdProduct as any);
      jest.spyOn(repository, 'save').mockResolvedValue(createdProduct as any);

      const result = await service.create(dto as any);
      expect(repository.create).toHaveBeenCalledWith(dto);
      expect(repository.save).toHaveBeenCalledWith(createdProduct);
      expect(result).toEqual(createdProduct);
    });
  });

  describe('findAll', () => {
    it('should return an array of products', async () => {
      const products = [
        { id: 1, name: 'Product 1', price: 50 },
        { id: 2, name: 'Product 2', price: 75 },
      ];
      jest.spyOn(repository, 'find').mockResolvedValue(products as any);

      const result = await service.findAll();
      expect(repository.find).toHaveBeenCalled();
      expect(result).toEqual(products);
    });
  });

  describe('findOne', () => {
    it('should return a single product by id', async () => {
      const product = { id: 1, name: 'Product 1', price: 50 };
      jest.spyOn(repository, 'findOne').mockResolvedValue(product as any);

      const result = await service.findOne(1);
      expect(repository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });
      expect(result).toEqual(product);
    });
  });

  describe('update', () => {
    it('should update and return the product', async () => {
      const existingProduct = { id: 1, name: 'Old', price: 10 };
      const updateDto = { name: 'New', price: 20 };
      const updatedProduct = { ...existingProduct, ...updateDto };

      jest.spyOn(repository, 'preload').mockResolvedValue(updatedProduct as any);
      jest.spyOn(repository, 'save').mockResolvedValue(updatedProduct as any);

      const result = await service.update(1, updateDto as any);
      expect(repository.preload).toHaveBeenCalledWith({ id: 1, ...updateDto });
      expect(repository.save).toHaveBeenCalledWith(updatedProduct);
      expect(result).toEqual(updatedProduct);
    });
  });

  describe('remove', () => {
    it('should remove the product', async () => {
      const product = { id: 1, name: 'Product', price: 10 };
      jest.spyOn(repository, 'findOne').mockResolvedValue(product as any);
      jest.spyOn(repository, 'remove').mockResolvedValue(product as any);

      const result = await service.remove(1);
      expect(repository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });
      expect(repository.remove).toHaveBeenCalledWith(product);
      expect(result).toEqual(product);
    });
  });
});