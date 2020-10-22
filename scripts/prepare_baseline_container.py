import time
import os

if __name__ == "__main__":
    baseline_dir = '/public/g_cluster/user_dir/baseline-ubuntu18.04-nvidia'
    # baseline_dir = '/var/lib/docker/overlay2/3531a2be4e046e593bd70abea318f3b257484f8b743fbb45f138ecf6b47bd8b6/merged/'
    prepared_baseline_dir = '/public/g_cluster/user_dir/prepared_baseline-ubuntu18.04-nvidia/'
    num_copies = 10
    print('Start making %d copies of: %s' %(num_copies, baseline_dir))
    print('Target directory: %s' % prepared_baseline_dir)
    init_offset = 0
    for i in range(num_copies):
        tic = time.time()    
        print('%3d / %-3d' %(i, num_copies), end='\t')

        target_path = os.path.join(prepared_baseline_dir, 'baseline-ubuntu18.04-nvidia__TMP__%02d' % (i+init_offset))
        while os.path.exists(target_path):
            init_offset += 1
            target_path = os.path.join(prepared_baseline_dir, 'baseline-ubuntu18.04-nvidia__TMP__%02d' % (i+init_offset))

        print(target_path)
        os.system('mkdir %s' % target_path)
        # copytree(baseline_path, target_path)
        # os.system('cp -ra %s %s' %(baseline_path, target_path))
        status = os.system(
            # 'ssh g01 '
            'cp -a '
            f'{baseline_dir}/bin '
            f'{baseline_dir}/etc '
            f'{baseline_dir}/lib '
            f'{baseline_dir}/lib64 '
            f'{baseline_dir}/opt '
            f'{baseline_dir}/root '
            f'{baseline_dir}/sbin '
            f'{baseline_dir}/usr '
            f'{target_path}/'
        )
        
        toc = time.time() - tic
        if status:
            print('Failed! Time: %d s' % toc)
            print('Cleaning...')
            os.system('rm -rf %s' % target_path)
            print('Finished!')
            break
        else:
            print('Done! Time: %d s' % toc)
        
