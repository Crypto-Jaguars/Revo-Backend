import { Test, TestingModule } from '@nestjs/testing';
import { StatusService } from './status.service';
import { OrderService } from './order.service';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Order, OrderStatus } from '../entities/order.entity';
import { Repository } from 'typeorm';
import { NotFoundException, BadRequestException } from '@nestjs/common';

const mockOrderService = {
  findOne: jest.fn(),
};

const mockOrderRepository = {
  save: jest.fn(),
};

describe('StatusService', () => {
  let service: StatusService;
  let orderService: OrderService;
  let orderRepository: Repository<Order>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        StatusService,
        {
          provide: OrderService,
          useValue: mockOrderService,
        },
        {
          provide: getRepositoryToken(Order),
          useValue: mockOrderRepository,
        },
      ],
    }).compile();

    service = module.get<StatusService>(StatusService);
    orderService = module.get<OrderService>(OrderService);
    orderRepository = module.get<Repository<Order>>(getRepositoryToken(Order));
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('updateOrderStatus', () => {
    it('should update the order status and history (valid transition)', async () => {
      const orderId = 'uuid-1';
      const newStatus = OrderStatus.COMPLETED;
      const existingOrder: Partial<Order> = {
        id: orderId,
        status: OrderStatus.PENDING, // Start in PENDING
        statusHistory: [],
      };

      mockOrderService.findOne.mockResolvedValue(existingOrder);
      mockOrderRepository.save.mockResolvedValue(existingOrder);

      await service.updateOrderStatus(orderId, newStatus);

      expect(mockOrderService.findOne).toHaveBeenCalledWith(orderId);
      expect(existingOrder.status).toBe(newStatus);
      expect(existingOrder.statusHistory).toEqual([
        { status: newStatus, timestamp: expect.any(Date) },
      ]);
      expect(mockOrderRepository.save).toHaveBeenCalledWith(existingOrder);
    });

    it('should initialize statusHistory if null', async () => {
      const orderId = 'uuid-2';
      const newStatus = OrderStatus.CANCELED;
      const existingOrder: Partial<Order> = {
        id: orderId,
        status: OrderStatus.PENDING,
        statusHistory: null, // Start with null history
      };

      mockOrderService.findOne.mockResolvedValue(existingOrder);
      mockOrderRepository.save.mockResolvedValue(existingOrder);

      await service.updateOrderStatus(orderId, newStatus);
      expect(existingOrder.statusHistory).not.toBeNull();
      expect(existingOrder.statusHistory).toHaveLength(1);
    });

    it('should add to existing status history', async() => {
      const orderId = '123';
        const newStatus = OrderStatus.COMPLETED;
        const existingOrder: Partial<Order> = {
          id: orderId,
          status: OrderStatus.PENDING,
          statusHistory: [{ status: OrderStatus.PENDING, timestamp: new Date() }],
        };

        mockOrderService.findOne.mockResolvedValue(existingOrder);
        mockOrderRepository.save.mockResolvedValue(existingOrder);
        await service.updateOrderStatus(orderId, newStatus);

        expect(existingOrder.statusHistory).toHaveLength(2);
        expect(mockOrderRepository.save).toHaveBeenCalledWith(existingOrder);
    })

    it('should throw NotFoundException if order does not exist', async () => {
      const orderId = 'non-existent-id';
      const newStatus = OrderStatus.COMPLETED;

      mockOrderService.findOne.mockResolvedValue(null);

      await expect(
        service.updateOrderStatus(orderId, newStatus),
      ).rejects.toThrow(NotFoundException);

      expect(mockOrderRepository.save).not.toHaveBeenCalled();
    });
    it('should throw BadRequestException for invalid status transitions', async () => {
      const orderId = 'uuid-4';
      const newStatus = OrderStatus.COMPLETED;
      const existingOrder: Partial<Order> = {
        id: orderId,
        status: OrderStatus.COMPLETED,
        statusHistory: [],
      };

      mockOrderService.findOne.mockResolvedValue(existingOrder);

      await expect(
        service.updateOrderStatus(orderId, newStatus),
      ).rejects.toThrow(BadRequestException);

        expect(mockOrderRepository.save).not.toHaveBeenCalled();
    });
    it('should allow PENDING -> CANCELED transition', async () => {
        const orderId = 'uuid-5';
        const newStatus = OrderStatus.CANCELED;
        const existingOrder: Partial<Order> = {
          id: orderId,
          status: OrderStatus.PENDING,
          statusHistory: [],
        };

        mockOrderService.findOne.mockResolvedValue(existingOrder);
        mockOrderRepository.save.mockResolvedValue(existingOrder);


        await service.updateOrderStatus(orderId, newStatus); // Should not throw

        expect(existingOrder.status).toBe(newStatus);
        expect(mockOrderRepository.save).toHaveBeenCalled();
    });

      it('should NOT allow COMPLETED -> PENDING transition', async () => {
        const orderId = 'uuid-6';
        const newStatus = OrderStatus.PENDING;
        const existingOrder: Partial<Order> = {
          id: orderId,
          status: OrderStatus.COMPLETED, // Start from COMPLETED
          statusHistory: [],
        };

        mockOrderService.findOne.mockResolvedValue(existingOrder);

        await expect(
          service.updateOrderStatus(orderId, newStatus),
        ).rejects.toThrow(BadRequestException);
        expect(mockOrderRepository.save).not.toHaveBeenCalled(); // Ensure save was not called

      });
      it('should NOT allow CANCELED -> PENDING transition', async () => {
            const orderId = 'uuid-6';
            const newStatus = OrderStatus.PENDING;
            const existingOrder: Partial<Order> = {
              id: orderId,
              status: OrderStatus.CANCELED, // Start from CANCELED
              statusHistory: [],
            };

            mockOrderService.findOne.mockResolvedValue(existingOrder);

            await expect(
              service.updateOrderStatus(orderId, newStatus),
            ).rejects.toThrow(BadRequestException);
            expect(mockOrderRepository.save).not.toHaveBeenCalled(); // Ensure save was not called
      });
    });
     describe('getOrderStatusHistory', () => {
    it('should return the order status history', async () => {
      const orderId = '123';
      const existingOrder: Partial<Order> = {
        id: orderId,
        status: OrderStatus.PENDING,
        statusHistory: [
          { status: OrderStatus.PENDING, timestamp: new Date() },
          { status: OrderStatus.COMPLETED, timestamp: new Date() },
        ],
      };

      mockOrderService.findOne.mockResolvedValue(existingOrder);

      const history = await service.getOrderStatusHistory(orderId);

      expect(mockOrderService.findOne).toHaveBeenCalledWith(orderId);
      expect(history).toEqual(existingOrder.statusHistory);
    });

    it('should return an empty array if no status history exists', async () => {
      const orderId = '123';
      const existingOrder: Partial<Order> = {
        id: orderId,
        status: OrderStatus.PENDING,
        statusHistory: null,
      };

      mockOrderService.findOne.mockResolvedValue(existingOrder);

      const history = await service.getOrderStatusHistory(orderId);

      expect(mockOrderService.findOne).toHaveBeenCalledWith(orderId);
      expect(history).toEqual([]);
    });

    it('should throw NotFoundException if order does not exist', async () => {
      const orderId = 'non-existent-id';

      mockOrderService.findOne.mockResolvedValue(null);

      await expect(service.getOrderStatusHistory(orderId)).rejects.toThrow(
        NotFoundException,
      );
    });
    });
});