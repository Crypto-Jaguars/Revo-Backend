import {
  Body,
  Controller,
  InternalServerErrorException,
  Post,
  Get,
  Delete,
  Put,
  NotFoundException,
  Param,
  Patch,
  Query,
  UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiQuery } from '@nestjs/swagger';
import { ParseDatePipe } from '../pipes/parse-date.pipe';
import { CreateOrderDto } from '../dtos/create-order.dto';
import { OrderService } from '../services/order.service';
import { UpdateOrderDto } from '../dtos/update-order.dto';
import { JwtAuthGuard } from '../../../modules/auth/guards/jwt-auth.guard';
import { OrderSchema } from '../../../docs/schemas/schemas'; // Ajusta la ruta

@ApiTags('orders')
@Controller('orders')
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @Post()
  @ApiOperation({ description: 'Creates a new order.' })
  @ApiResponse({ status: 201, description: 'Order created successfully.', type: OrderSchema })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async create(@Body() createOrderDto: CreateOrderDto) {
    try {
      return this.orderService.create(createOrderDto);
    } catch (error) {
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Get()
  @ApiOperation({ description: 'Retrieves a list of all orders.' })
  @ApiResponse({ status: 200, description: 'List of orders retrieved successfully.', type: [OrderSchema] })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async findAll() {
    try {
      return await this.orderService.findAll();
    } catch (error) {
      if (error instanceof InternalServerErrorException) {
        throw new InternalServerErrorException(error.message);
      }
      throw error;
    }
  }

  @Get(':id')
  @ApiOperation({ description: 'Retrieves a specific order by ID.' })
  @ApiResponse({ status: 200, description: 'Order retrieved successfully.', type: OrderSchema })
  @ApiResponse({ status: 404, description: 'Order not found.' })
  async findOne(@Param('id') id: string) {
    try {
      return await this.orderService.findOne(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw error;
    }
  }

  @Patch('cancel/:id')
  @ApiOperation({ description: 'Cancels a specific order by ID.' })
  @ApiResponse({ status: 200, description: 'Order cancelled successfully.', type: OrderSchema })
  @ApiResponse({ status: 404, description: 'Order not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async cancel(@Param('id') id: string) {
    try {
      return await this.orderService.cancel(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to cancel order');
    }
  }

  @Put(':id')
  @ApiOperation({ description: 'Updates a specific order by ID.' })
  @ApiResponse({ status: 200, description: 'Order updated successfully.', type: OrderSchema })
  @ApiResponse({ status: 404, description: 'Order not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async update(
    @Param('id') id: string,
    @Body() updateOrderDto: UpdateOrderDto,
  ) {
    try {
      return await this.orderService.update(id, updateOrderDto);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to update order');
    }
  }

  @Delete(':id')
  @ApiOperation({ description: 'Deletes a specific order by ID.' })
  @ApiResponse({ status: 200, description: 'Order deleted successfully.' })
  @ApiResponse({ status: 404, description: 'Order not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async remove(@Param('id') id: string) {
    try {
      return await this.orderService.remove(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to delete order');
    }
  }

  @Get('reports/sales')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ description: 'Generates a sales report for orders within a date range.' })
  @ApiQuery({ name: 'startDate', required: true, description: 'Start date of the range (YYYY-MM-DD)' })
  @ApiQuery({ name: 'endDate', required: true, description: 'End date of the range (YYYY-MM-DD)' })
  @ApiResponse({ status: 200, description: 'Sales report generated successfully.' })
  @ApiResponse({ status: 401, description: 'Unauthorized.' })
  @ApiResponse({ status: 404, description: 'Not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async getSalesReport(
    @Query('startDate', new ParseDatePipe()) startDate: Date,
    @Query('endDate', new ParseDatePipe()) endDate: Date,
  ) {
    try {
      return this.orderService.getSalesReport(
        startDate.toISOString(),
        endDate.toISOString(),
      );
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to generate sales report');
    }
  }

  @Get('reports/metrics')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ description: 'Retrieves order metrics within a date range.' })
  @ApiQuery({ name: 'startDate', required: true, description: 'Start date of the range (YYYY-MM-DD)' })
  @ApiQuery({ name: 'endDate', required: true, description: 'End date of the range (YYYY-MM-DD)' })
  @ApiResponse({ status: 200, description: 'Order metrics retrieved successfully.' })
  @ApiResponse({ status: 401, description: 'Unauthorized.' })
  @ApiResponse({ status: 404, description: 'Not found.' })
  @ApiResponse({ status: 500, description: 'Internal server error.' })
  async getOrderMetrics(
    @Query('startDate', new ParseDatePipe()) startDate: Date,
    @Query('endDate', new ParseDatePipe()) endDate: Date,
  ) {
    try {
      return this.orderService.getOrderMetrics(
        startDate.toISOString(),
        endDate.toISOString(),
      );
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw new NotFoundException(error.message);
      }
      throw new InternalServerErrorException('Failed to retrieve order metrics');
    }
  }
}