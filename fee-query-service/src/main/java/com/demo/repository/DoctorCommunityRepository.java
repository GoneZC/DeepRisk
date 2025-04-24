package com.demo.repository;

import com.demo.model.DoctorCommunity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DoctorCommunityRepository extends JpaRepository<DoctorCommunity, String> {
    DoctorCommunity findByBilgDrCode(String doctorCode);
} 