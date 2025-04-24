import { BaseEntity, ManyToOne } from 'typeorm';
import {
  Entity,
  Column,
  OneToMany,
  DeleteDateColumn,
  PrimaryGeneratedColumn,
  CreateDateColumn,
} from 'typeorm';
import { OrderItem } from './order-item.entity';

export interface ProductSnapshot {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image: string;
}

export enum OrderStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  CANCELED = 'canceled',
}

@Entity('orders')
export class Order extends BaseEntity {
  @Column({ type: 'int', nullable: false })
  userId: number;

  @Column('decimal', { precision: 10, scale: 2, nullable: false })
  totalAmount: number;

  @Column({ default: OrderStatus.PENDING, nullable: false })
  status: OrderStatus;

  @Column({ type: 'varchar', length: 255, nullable: false })
  stellarTransactionHash: string;

  @Column({ type: 'varchar', length: 255, nullable: false })
  stellarPublicKey: string;

  @Column({ type: 'timestamp', nullable: false })
  paymentDeadline: Date;

  @OneToMany(() => OrderItem, (orderItem: { order: any }) => orderItem.order, {
    cascade: true,
  })
  items: OrderItem[];

  @Column('simple-json', { nullable: true })
  metadata: Record<string, any>;

  @DeleteDateColumn({ nullable: true })
  deletedAt: Date;

  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  customerId: number;

  @CreateDateColumn()
  createdAt: Date;

  @Column('jsonb')
  productSnapshot: ProductSnapshot;

  @ManyToOne(() => Order, (order) => order.items)
  order: Order;

  @Column({ type: 'jsonb', default: [] })
  statusHistory: { status: OrderStatus; timestamp: Date }[];
}
