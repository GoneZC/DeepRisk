package com.demo.dto;

import java.util.List;

public class SearchRequest {
    private List<String> medTypes;
    private String mdtrtId;
    private String psnNo;
    private int page;
    private int size;
    
    // getters and setters
    public List<String> getMedTypes() { return medTypes; }
    public void setMedTypes(List<String> medTypes) { this.medTypes = medTypes; }
    public String getMdtrtId() { return mdtrtId; }
    public void setMdtrtId(String mdtrtId) { this.mdtrtId = mdtrtId; }
    public String getPsnNo() { return psnNo; }
    public void setPsnNo(String psnNo) { this.psnNo = psnNo; }
    public int getPage() { return page; }
    public void setPage(int page) { this.page = page; }
    public int getSize() { return size; }
    public void setSize(int size) { this.size = size; }
}