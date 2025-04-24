/* eslint-disable prettier/prettier */
import {
  Entity,
  Column,
  PrimaryGeneratedColumn,
  CreateDateColumn,
} from 'typeorm';

@Entity()
export class Sales {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  orderId: number;

  @Column('decimal')
  totalAmount: number;

  @CreateDateColumn()
  createdAt: Date;
}
