#[cfg(test)]
mod test {
    use crate::{CSAMembershipContract, CSAMembershipContractClient, ShareSize};
    use soroban_sdk::{
        testutils::{Address as TestAddress, Events},
        Env, BytesN, String, Symbol,
    };
    use soroban_sdk::TryFromVal;
    use std::vec; // Importa la macro vec! de std

    #[test]
    fn test_enroll_membership() {
        let env = Env::default();
        let contract_id = env.register(CSAMembershipContract, ()); // Registro del contrato
        let client = CSAMembershipContractClient::new(&env, &contract_id);

        let farm_id = BytesN::from_array(&env, &[0; 32]);
        let season = String::from_str(&env, "Summer 2023");
        let share_size = ShareSize::Medium;
        let pickup_location = String::from_str(&env, "Farm Market");
        let start_date = env.ledger().timestamp() + 86400; // Mañana
        let end_date = start_date + 86400 * 90; // 90 días después
        let member = TestAddress::generate(&env);

        client.enroll_membership(&farm_id, &season, &share_size, &pickup_location, &start_date, &end_date, &member);

        let events = env.events().all();
        assert_eq!(events.len(), 1); // Solo un evento por inscripción
        let event = events.get_unchecked(0);
        let topics: ::std::vec::Vec<Symbol> = event.1.iter().map(|val| Symbol::try_from_val(&env, &val).unwrap()).collect();
        assert_eq!(
            topics,
            vec![
                Symbol::new(&env, "enroll_membership"),
                Symbol::new(&env, "success"),
            ]
        );
    }

    #[test]
    fn test_update_pickup_location() {
        let env = Env::default();
        let contract_id = env.register(CSAMembershipContract, ()); // Registro del contrato
        let client = CSAMembershipContractClient::new(&env, &contract_id);

        let farm_id = BytesN::from_array(&env, &[0; 32]);
        let season = String::from_str(&env, "Summer 2023");
        let share_size = ShareSize::Medium;
        let pickup_location = String::from_str(&env, "Farm Market");
        let start_date = env.ledger().timestamp() + 86400;
        let end_date = start_date + 86400 * 90;
        let member = TestAddress::generate(&env);

        client.enroll_membership(&farm_id, &season, &share_size, &pickup_location, &start_date, &end_date, &member);

        let token_id = BytesN::from_array(&env, &[0; 32]);
        let new_location = String::from_str(&env, "City Market");
        client.update_pickup_location(&token_id, &new_location, &member);

        let membership = client.get_membership_metadata(&token_id).expect("Membership not found");
        assert_eq!(membership.pickup_location, new_location);

        let events = env.events().all();
        assert_eq!(events.len(), 2); // Dos eventos: inscripción + actualización
        let event = events.get_unchecked(1); // Verifica el evento de actualización
        let topics: ::std::vec::Vec<Symbol> = event.1.iter().map(|val| Symbol::try_from_val(&env, &val).unwrap()).collect();
        assert_eq!(
            topics,
            vec![
                Symbol::new(&env, "update_pickup_location"),
                Symbol::new(&env, "success"),
            ]
        );
    }

    #[test]
    fn test_cancel_membership() {
        let env = Env::default();
        let contract_id = env.register(CSAMembershipContract, ()); // Registro del contrato
        let client = CSAMembershipContractClient::new(&env, &contract_id);

        let farm_id = BytesN::from_array(&env, &[0; 32]);
        let season = String::from_str(&env, "Summer 2023");
        let share_size = ShareSize::Medium;
        let pickup_location = String::from_str(&env, "Farm Market");
        let start_date = env.ledger().timestamp() + 86400;
        let end_date = start_date + 86400 * 90;
        let member = TestAddress::generate(&env);

        client.enroll_membership(&farm_id, &season, &share_size, &pickup_location, &start_date, &end_date, &member);

        let token_id = BytesN::from_array(&env, &[0; 32]);
        client.cancel_membership(&token_id, &member);

        let membership = client.get_membership_metadata(&token_id);
        assert!(membership.is_none());

        let events = env.events().all();
        assert_eq!(events.len(), 2); // Dos eventos: inscripción + cancelación
        let event = events.get_unchecked(1); // Verifica el evento de cancelación
        let topics: ::std::vec::Vec<Symbol> = event.1.iter().map(|val| Symbol::try_from_val(&env, &val).unwrap()).collect();
        assert_eq!(
            topics,
            vec![
                Symbol::new(&env, "cancel_membership"),
                Symbol::new(&env, "success"),
            ]
        );
    }
}