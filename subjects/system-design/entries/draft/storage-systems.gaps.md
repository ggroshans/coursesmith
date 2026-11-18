# storage-systems gaps (pass b10)
- RAM and ROM, USB drive, SD card: the ByteByteGo guide "types-of-memory-and-storage" is only a two-bullet list of names and gets no entry; suggested page: Random-access memory, Read-only memory.
- Volatile versus non-volatile memory has no page of its own in the crawl; suggested page: Volatile memory, Non-volatile memory.
- Hard disk drive versus solid-state drive trade-offs (seek time, wear, cost): suggested page: Solid-state drive (Hard disk drive is crawled but belongs to another chapter).
- Network file protocols (NFS, SMB) and iSCSI/Fibre Channel are named but not explained: suggested pages: Network File System, Server Message Block, iSCSI, Fibre Channel.
- Distributed file systems in general (GFS, HDFS design with NameNode/DataNode): suggested page: Distributed file system, Google File System.
- Amazon S3 (buckets, keys, the S3 API) as a product interviews name: suggested page: Amazon S3.
- Reed-Solomon error correction (the code behind most storage erasure coding): suggested page: Reed-Solomon error correction.
- Hot, warm and cold data and storage tiering: suggested page: Data tiering, Hot data.
- Data durability and "nines" of durability (11 nines vs 6 nines is cited but not explained): suggested page: Durability (computer science), Data integrity.
- Block-level storage and logical volumes as their own concepts: suggested pages: Block (data storage), Logical volume management.
- Cloud storage gateways and unified file-and-object storage: suggested page: Cloud storage gateway.
- Object-based storage device (OSD) standards and object-based file systems (metadata servers plus object servers): suggested pages: Object-based storage device, Ceph (software), Lustre (file system).

# storage-systems gaps (gap-fill batch gf09, chunks 04-08)
- Write-ahead log: the Durability entry names it and teaches it only in two facts; the page "Write-ahead logging" is crawled for another chapter and owns the title "Write-ahead log".
- Data tiering, hot/warm/cold data and storage tiers: no page in the crawl; Amazon S3 storage classes and tape are the only hints. Suggested pages: Data tiering, Hierarchical storage management.
- Magnetic tape data storage (archival and backup media): only Non-volatile memory and Backup mention tape; suggested page: Magnetic tape data storage.
- Storage area network and Network-attached storage as their own pages (Fibre Channel, iSCSI, NFS and SMB entries cover the protocols; the architecture lives in "DAS, NAS and SAN"): suggested pages: Storage area network, Network-attached storage.
- NVM Express, SCSI and TRIM have no pages of their own (they are covered by sentences of SSD, HDD and iSCSI): suggested pages: NVM Express, Trim (computing), Write amplification.
- Distributed and parallel file systems (Ceph, Lustre, GPFS) are only named in the NFS and SMB pages: suggested pages: Ceph (software), Lustre (file system), Distributed file system.
- Block (data storage), logical volume management and cloud storage gateway remain unexplained: suggested pages: Block (data storage), Logical volume management, Cloud storage gateway.
- Erasure coding in systems (Cauchy and Vandermonde matrices, local reconstruction codes) is only named: suggested page: Locally repairable code.
