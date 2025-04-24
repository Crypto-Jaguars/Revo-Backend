/* eslint-disable prettier/prettier */
import { Injectable } from '@nestjs/common';
import { InternalServerErrorException } from '@nestjs/common';
import { OrderService } from '../services/order.service';

@Injectable()
export class DashboardService {
  constructor(private readonly orderService: OrderService) {}

  async fetchDashboardData(startDate: string, endDate: string) {
    try {
      const salesReport = await this.orderService.getSalesReport(
        startDate,
        endDate,
      );
      const orderMetrics = await this.orderService.getOrderMetrics(
        startDate,
        endDate,
      );

      return {
        salesReport,
        orderMetrics,
      };
    } catch (error) {
      throw new InternalServerErrorException(
        'Failed to fetch dashboard data',
        error.message,
      );
    }
  }
}
