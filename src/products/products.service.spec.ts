import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ProductsService } from './products.service';
import { Product } from './entities/product.entity';
import { NotFoundException } from '@nestjs/common';
import { CreateProductDto } from './dto/create-product.dto'; // Add this import

describe('ProductsService', () => {
  let service: ProductsService;
  let repository: Repository<Product>;

  beforeEach(async () => {
    const repositoryMock = {
      create: jest.fn(),
      save: jest.fn(),
      find: jest.fn(),
      findOne: jest.fn(),
      preload: jest.fn(),
      softDelete: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ProductsService,
        {
          provide: getRepositoryToken(Product),
          useValue: repositoryMock,
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
      // Update dto to include all required fields from CreateProductDto
      const dto: CreateProductDto = { 
        name: 'Test Product', 
        price: 100, 
        category: 'Fruit',      // example required field
        farmerId: '123e4567-e89b-12d3-a456-426614174000', // changed to valid UUID string
        priceUnit: 'kg',        // added required field
        stockQuantity: 50       // added required field
      };
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
    it('should soft delete the product', async () => {
      const product = { id: 1, name: 'Product', price: 10, deletedAt: null };

      jest.spyOn(repository, 'findOne').mockResolvedValue(product as any);
      const softDeleteMock = jest.spyOn(repository, 'softDelete').mockResolvedValue({} as any);

      const result = await service.remove(1);
      expect(repository.findOne).toHaveBeenCalledWith({ where: { id: 1 } });
      expect(softDeleteMock).toHaveBeenCalledWith(1);
      expect(result).toBeUndefined();
    });
  });

  describe('findByFarmer', () => {
    it('should return products filtered by farmerId', async () => {
      const farmerId = '123e4567-e89b-12d3-a456-426614174000'; // Use a valid UUID string
      const products = [
        { id: 1, name: 'Apple', price: 10, farmerId },
        { id: 2, name: 'Banana', price: 15, farmerId },
      ];
      jest.spyOn(repository, 'find').mockResolvedValue(products as any);

      const result = await service.findByFarmer(farmerId);
      expect(repository.find).toHaveBeenCalledWith({ where: { farmerId } });
      expect(result).toEqual(products);
    });
  });

  describe('findByCategory', () => {
    it('should return products filtered by category', async () => {
      const category = 'Fruit';
      const products = [
        { id: 1, name: 'Apple', price: 10, category },
        { id: 2, name: 'Banana', price: 15, category },
      ];
      jest.spyOn(repository, 'find').mockResolvedValue(products as any);

      const result = await service.findByCategory(category);
      expect(repository.find).toHaveBeenCalledWith({ where: { category } });
      expect(result).toEqual(products);
    });
  });

  describe('Edge Cases', () => {
    it('findOne should throw NotFoundException if product not found', async () => {
      jest.spyOn(repository, 'findOne').mockResolvedValue(null as any);
      await expect(service.findOne(999)).rejects.toThrowError(NotFoundException);
    });

    it('update should throw NotFoundException if product not found', async () => {
      jest.spyOn(repository, 'preload').mockResolvedValue(null as any);
      await expect(service.update(999, { name: 'X' } as any)).rejects.toThrowError(NotFoundException);
    });

    it('remove should throw NotFoundException if product not found', async () => {
      jest.spyOn(repository, 'findOne').mockResolvedValue(null as any);
      await expect(service.remove(999)).rejects.toThrowError(NotFoundException);
    });

    it('create should throw error for invalid input', async () => {
      // Simulate validation error by throwing in repository.create
      jest.spyOn(repository, 'create').mockImplementation(() => { throw new Error('Validation failed'); });
      await expect(service.create({} as any)).rejects.toThrow('Validation failed');
    });

    it('update should throw error for invalid input', async () => {
      // Simulate validation error by throwing in repository.preload
      jest.spyOn(repository, 'preload').mockImplementation(() => { throw new Error('Validation failed'); });
      await expect(service.update(1, {} as any)).rejects.toThrow('Validation failed');
    });

    it('findByFarmer should return empty array if no products found', async () => {
      jest.spyOn(repository, 'find').mockResolvedValue([]);
      const result = await service.findByFarmer('non-existent-farmer');
      expect(result).toEqual([]);
    });

    it('findByCategory should return empty array if no products found', async () => {
      jest.spyOn(repository, 'find').mockResolvedValue([]);
      const result = await service.findByCategory('non-existent-category');
      expect(result).toEqual([]);
    });
  });
});