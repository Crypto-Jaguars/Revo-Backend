import { BaseEntity } from './../../../shared/entities/base.entity';
import { Entity, Column, DeleteDateColumn, Index, ManyToOne, JoinColumn } from 'typeorm';
import { Category } from './category.entity';

@Entity('products')

export class Product extends BaseEntity {
  @Index() // Adding an index to speed up searches by name
  @Column({ type: 'varchar', length: 255, nullable: false })
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string;

  @Column({ type: 'decimal', precision: 10, scale: 2, nullable: false })
  price: number;

  @Column()
  unit: string;

  @Column('simple-json', { nullable: true })
  images: string[];

  @Column()
  stockQuantity: number;

  @ManyToOne(() => Category, (category) => category.products, {
    nullable: false,
  })
  @JoinColumn({ name: 'categoryId' })
  category: Category;

  @Column({ type: 'timestamp' })
  harvestDate: Date;

  @DeleteDateColumn({ nullable: true })
  deletedAt: Date;
}