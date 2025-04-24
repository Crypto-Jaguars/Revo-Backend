import { Entity, Column, ManyToOne, PrimaryGeneratedColumn } from 'typeorm';
import { Order } from './order.entity';

@Entity('order_items')
export class OrderItem {
  @ManyToOne(() => Order, (order) => order.items, { onDelete: 'CASCADE' })
  order: Order;

  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ nullable: false })
  productId: string;

  @Column({ type: 'int', nullable: false })
  quantity: number;

  @Column('decimal', { precision: 10, scale: 2, nullable: false })
  pricePerUnit: number;

  @Column('decimal', { precision: 10, scale: 2, nullable: false })
  totalPrice: number;

  @Column('jsonb')
  productSnapshot: any;
}
