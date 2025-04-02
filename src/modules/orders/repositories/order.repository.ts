/* eslint-disable prettier/prettier */
import { Repository } from 'typeorm';
import { BadRequestException } from '@nestjs/common';
import { Order } from '../entities/order.entity';

import { Injectable } from '@nestjs/common';

@Injectable()
export class OrderRepository extends Repository<Order> {
  async getSalesReport(
    startDate: string,
    endDate: string,
  ): Promise<{ totalSales: string }> {
    if (
      !this.isValidDateFormat(startDate) ||
      !this.isValidDateFormat(endDate)
    ) {
      throw new BadRequestException('Invalid date format. Use YYYY-MM-DD');
    }

    return this.createQueryBuilder('order')
      .select('SUM(order.amount)', 'totalSales')
      .where('order.createdAt BETWEEN :startDate AND :endDate', {
        startDate,
        endDate,
      })
      .getRawOne();
  }

  
  async getOrderMetrics(
    startDate: string,
    endDate: string,
  ): Promise<{ totalOrders: string; averageOrderAmount: string }> {

    if (
      !this.isValidDateFormat(startDate) ||
      !this.isValidDateFormat(endDate)
    ) {
      throw new BadRequestException('Invalid date format. Use YYYY-MM-DD');
    }

    return this.createQueryBuilder('order')
      .select('COUNT(order.id)', 'totalOrders')
      .addSelect('AVG(order.amount)', 'averageOrderAmount')
      .where('order.createdAt BETWEEN :startDate AND :endDate', {
        startDate,
        endDate,
      })
      .getRawOne();
  }
      

  private isValidDateFormat(dateString: string): boolean {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    return regex.test(dateString) && !isNaN(Date.parse(dateString));
  }
}
